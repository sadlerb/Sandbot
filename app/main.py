import os
import sys
import time
import random
from datetime import datetime
from app import db, bot
from app.database import *
from app.request_manager import *
from discord.ext import commands, tasks
from discord.ext.commands.errors import MissingRequiredArgument
from discord import Game
import asyncio
import discord
from discord.errors import HTTPException

sad_words = ['sad','depressed','unhappy','miserable','angry','depressing','miserable','fucked']

# EVENTS

# When bot is logged in and ready
@bot.event
async def on_ready():
  await bot.change_presence(activity=Game(name='$commands'))
  sys.stdout.write('We have logged in as {0.user}'.format(bot))
  sys.stdout.flush()
  daily_word.start()

# On message in text channel
@bot.event
async def on_message(message):
  if message.author == bot.user:
    return
  
  if any(word.lower() in message.content for word in sad_words):
    response = getRandomEntry(db['messages'])
    await message.channel.send(response['message'])
    sys.stdout.write('A user has been encouraged')
    sys.stdout.flush()
  await bot.process_commands(message)

# On text channel message deleted
@bot.event
async def on_message_delete(message):
  if message.author == bot.user:
    return
  
  await message.channel.send('I saw that delete ' + message.author.name + '. What are you hiding?')
  print_log('A user was sus.')

# On text channel message edited
@bot.event
async def on_message_edit(before,after):
  if before.author == bot.user:
    return
  await after.channel.send('I saw that edit '  + after.author.name + '.')
  print_log('A user has been warned')

# Command error handeling
@bot.event
async def on_command_error(ctx,error):
  if isinstance(error,commands.CommandOnCooldown):
    await ctx.send('** Still on cooldown**. Please try again in {:.2f}s'.format(error.retry_after),delete_after=3)

# TASKS

# Send Urban Dictionary word of the day to text channel
@tasks.loop(hours=24)
async def daily_word():
  result = get_daily_urban_word()
  message = '**Word of the Day** \n\n***%s*** \n\n%s \n\n*%s* ' % (result['word'],result['meaning'],result['example'])
  embed = discord.Embed(title=result['word'],url=result['url'],description= 'Urban Dictionary ' + result['word'])
  message_channel = bot.get_channel(839259915049893938)
  await message_channel.send(message,embed=embed)
  print_log('Daily Word sent')

# Before daily_word
@daily_word.before_loop
async def before():
  await bot.wait_until_ready()

# COMMANDS

# The bot inspires the user with a quote upon request
@bot.command()
async def inspire(ctx):
  quote = get_inspiration()
  await ctx.send(quote)
  print_log('A user has been inspired')
    

# The users message is added to the database
@bot.command(name='new')
async def save_quote(ctx, *, arg):
  collection = db["messages"]
  newMessage = arg.strip()
  if collection.estimated_document_count() == 0: # if there is no quotes in the database
    order = 1
  else:
    last_entry = getLastEntry(collection)
    order = last_entry[0]['order'] + 1    

  post = {'message':newMessage,'order':order}
  collection.insert_one(post)
  await ctx.send('The Sandbot will remember that',delete_after=5)
  print_log('Sandbot has remembered')

# The bot lists all quotes stored in the database 
@bot.command(name='list')
async def getlist(ctx):
  quoteString = ''
  quoteList = getAllEntries(db['messages'])
  for quote in quoteList:
    quoteString = quoteString + str(quote['order']) + ' )  ' + quote['message'] + '\n'

  response = "```" + quoteString + "```"
  await ctx.send(response)
  print_log('The quotes have been delivered')

# The bot deletes the quote specified by the user
@bot.command(name='del')
async def delete(ctx,arg):
  collection = db["messages"]
  _order =  arg
  try:
      order = int(_order)
      if document_exists(collection,order,'order') : # determines if the requested document exists
        quoteList = collection.find().skip(order-1) # skips pointer to just before specified document
        if order <= collection.count_documents({}) : # I don't remember why this was necessary
          results = collection.delete_one({"order":order})
          for x in quoteList: # rearanges the quotes in the collection after delete
            query = { "order": x['order'] }
            newvalues = { "$set": { "order": x['order'] - 1 }}
            collection.update_one(query,newvalues)
          await ctx.send('Quote deleted',delete_after=5)
        else:
          await ctx.send('That quote does not exist.',delete_after=5)
          sys.stdout.write('The requested quote was not found')
  except ValueError: # If a string is given insted of int
    await ctx.send('Please make sure the id is correct and try again.',delete_after=5)
  except MissingRequiredArgument: # if argument is missing
    await ctx.send('Please insert the number of the quote you want deleted',delete_after=5)
  print_log('Quote deleted')


# Gets news and sends it the specfied channel
@bot.command()
async def news(ctx):
  response = get_news()
  news_array = response[0]
  number = response[1]
  now = datetime.now().strftime('%d-%m-%Y at %H:%M')
  await ctx.send('Beginning of articles for ' + now )
  for article in news_array: # sends each article with a delay to avoid chat cooldowns
    time.sleep(5)
    await ctx.send('\n ' + ':newspaper: | ' + article)
  await ctx.send( str(number) + ' articles sent at ' + now)
  print_log('News has been delivered')

# The bot makes a decision for the user
@bot.command()
async def decide(ctx, *, args):
  choices = args.split('?')
  await ctx.send('Sandbot thinks you should ' + random.choice(choices))
  print_log('Sandbot made a very difficult decision')


# The bot deletes the specified amount of messages from the text channel
@bot.command()
async def clean(ctx,amount):
  amount = int(amount)
  if amount > 98 or amount < 1:
    await ctx.send('Please enter a number between 1 and 98',delete_after=5)
    return 
  await ctx.send('Add reaction 👍 to confirm',delete_after=10) # waits for confirmation from user before deleteing
  def check (reaction,user):
    return user == ctx.message.author and str(reaction.emoji) == '👍'

  try:
    reaction,user = await bot.wait_for('reaction_add',timeout=10,check=check) # waits 10 seconds for reaction

  except ValueError: # on non int value given
    ctx.channel.send('Please enter a number',delete_after=5)

  except asyncio.TimeoutError: # on timeout
    await ctx.send('Method aborted',delete_after=5)

  except MissingRequiredArgument: # on no amount given 
    await ctx.send('No amount was given. Aborting process',delete_after=5)
    
  else:
    mgs = []
    async for m in ctx.channel.history(limit=amount+2):
      mgs.append(m)
    await ctx.channel.delete_messages(mgs)
    await ctx.send('The evidence has been removed',delete_after=5)
    print_log('Some evidence was removed')


# Searches for the users message on the specified engine
@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def search(ctx, *, args):
  try:
    await ctx.send('Searching ...',delete_after=2)
    arguments = args.split(' ')
    query = ' '
    search_engine = arguments[0].lower()


    if 'wik' in search_engine: # Wiki search
      result = wikiSearch(query.join(arguments[1:]))
      if result['response'] == 1:
        message = '**' + result['title'] + '**\n\n' + result['extract']
        embed = discord.Embed(title=result['title'],url=result['url'],description='Wikipedia ' + result['title'])
        await ctx.send(message,embed=embed)
      else:
        message = "No results were found on Wikipedia."
        await ctx.send(message)


    elif 'goog' in search_engine: # google search
      result = googleSearch((query.join(arguments[1:])))
      await ctx.send('\n'.join(result))


    elif 'urb' in search_engine: # urban dictionary search 
      result = urbanSearch(query.join(arguments[1:]))
      if result['response'] == 1:
        message = '**%s** \n\n%s \n\n*%s* ' % (result['word'],result['meaning'],result['example'])
        embed = discord.Embed(title=result['word'],url=result['url'],description= 'Urban Dictionary ' + result['word'])
        await ctx.send(message,embed=embed)
      else:
        await ctx.send('Word was not found on Urban Dictionary')

    else: # google search if requsted engine is not recongised
      result = googleSearch((query.join(args)))
      await ctx.send('\n'.join(result))
  except HTTPException: # google search args if error occurs
      result = googleSearch((query.join(args)))
      await ctx.send('\n'.join(result))
  except Exception as err:
    exception_type = type(err).__name__
    print_log(exception_type)

  print_log('A user has requested knowleage.')

# The bot displays its commands
@bot.command(name='commands')
async def get_commands(ctx):
  commands = '''
  **$inspire** - Receive a inspiring message
  $new 'quotehere' - Add a new sentence to my vocabulary
  $list - View my current vocabulary
  $del 'quoteid' - Delete a sentense from my vocabulary
  $news - Get latest news articles
  $decide choice1?choice2?choicex - I will use advanced AI technology to select the right choice for you
  $clean 'amount' - I will delete amount number of messages. Limit = 98
  $search 'engine' 'query' - I will search for whatever you tell me to on the requested engine(5 second cooldown). Default google when no engine is found
  Current engines are google, wikipedia and urban dictionary
  I will randomly pop in from time to time on certain comments
  '''
  response = '```' + commands + '```'
  await ctx.send(response)
  print_log('Sandbots commands have been delivered')






def print_log(message):
  sys.stdout.write(message)
  sys.stdout.flush()

