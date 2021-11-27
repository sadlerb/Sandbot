import time, random, sys, os
from datetime import datetime, timedelta
from app import db, bot
from app.database import *
from app.request_manager import *
from discord.ext import commands, tasks
from discord.ext.commands.errors import MissingRequiredArgument
from discord import Game
import asyncio
import discord
from discord.errors import HTTPException
import sched
from discord.utils import get

sad_words = ['sad','depressed','unhappy','miserable','angry','depressing','miserable','fucked','shit']

# EVENTS

# When bot is logged in and ready
@bot.event
async def on_ready():
  await bot.change_presence(activity=Game(name='$commands'))
  sys.stdout.write('We have logged in as {0.user}'.format(bot))
  sys.stdout.flush()
  daily_word.start()
  start_sale.start()
    


# On message in text channel
'''@bot.event
async def on_message(message):
  if message.author == bot.user:
    return
  
  if any(word.lower() in message.content for word in sad_words):
    response = getRandomEntry(db['messages'])
    await message.channel.send(response['message'])
    sys.stdout.write('A user has been encouraged')
  await bot.process_commands(message)''' 

# On text channel message deleted
""" @bot.event
async def on_message_delete(message):
  if message.author == bot.user:
    return
  
  await message.channel.send('I saw that delete ' + message.author.name + '. What are you hiding?')
  print_log('A user was sus.') """

# On text channel message edited
""" @bot.event
async def on_message_edit(before,after):
  if before.author == bot.user:
    return
  await after.channel.send('I saw that edit '  + after.author.name + '.')
  print_log('A user has been warned')
 """
# Command error handeling
@bot.event
async def on_command_error(ctx,error):
  if isinstance(error,commands.CommandOnCooldown):
    await ctx.send('** Still on cooldown**. Please try again in {:.2f}s'.format(error.retry_after),delete_after=3)
  if isinstance(error,commands.CommandNotFound):
    await ctx.send('Command not found please check the command and try again.',delete_after=6)
  else:
    print(error)
    sys.stdout.flush()

# TASKS

# Send Urban Dictionary word of the day to text channel
@tasks.loop(hours=24)
async def daily_word():
  try:
    ctx = bot.get_channel(839259915049893938)
    result = get_daily_urban_word()
    message = '**Word of the Day** \n\n***%s*** \n\n%s \n\n*%s* ' % (result['word'],result['meaning'],result['example'])
    embed = discord.Embed(title=result['word'],url=result['url'],description= 'Urban Dictionary ' + result['word'])

    await ctx.send(message,embed=embed)
    print_log('Daily Word sent')
  except Exception as e:
    print(e)
    print_log('An error as occured')
    pass
  

@tasks.loop(count=1)
async def start_sale():
  ctx = bot.get_channel(842119883625594940)
  await saleInfo(ctx,discord)

# Before daily_word
@daily_word.before_loop
async def before():
  await bot.wait_until_ready()

@start_sale.before_loop
async def before():
  await bot.wait_until_ready()


# COMMANDS

# The bot inspires the user with a quote upon request
@bot.command()
async def inspire(ctx):
  quote = get_inspiration()
  await ctx.send(quote)
  print_log('A user has been inspired')

@bot.command(aliases=['deals'])
async def deal(ctx):
  deals = getalldeals()
  for i in deals:
    embed = discord.Embed(title=i[0],description='Normal Price: ' + i[1] + '\nSale Price: ' + i[2] + '\nRating: ' + i[3] + ' ' + i[4])
    embed.set_image(url=i[5])
    await ctx.send(embed=embed)
    time.sleep(3)
@bot.command(aliases=['find']) 
async def lookup(ctx,*,arg):
  result = deallookup(arg)
  for game in result:
    embed = discord.Embed(title=game['title'],description="Lowest Price: " + game['lowest'])
    embed.set_image(url=game['img'])
    await ctx.send(embed=embed)
    


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
    time.sleep(3)
    embed = discord.Embed(title=':newspaper: | ' + article['title'], description=article['desc'],url=article['url'])
    if article['image'] is not None:
      embed.set_image(url=article['image'])
    await ctx.send(embed=embed)
  await ctx.send( str(number) + ' articles sent at ' + now)
  print_log('News has been delivered')

# The bot makes a decision for the user
@bot.command()
async def decide(ctx, *, args):
  choices = args.split('?')
  await ctx.send('Sandbot picks ' + random.choice(choices))
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
async def search(ctx, args, engine,num=1):
  try:
    await ctx.send('Searching ...',delete_after=2)
    search_engine = engine.lower()


    if 'wi' in search_engine: # wiki search
      result = wikiSearch(args)
      if result['response'] == 1:
        message = '**' + result['title'] + '**\n\n' + result['extract']
        embed = discord.Embed(title=result['title'],url=result['url'],description='Wikipedia ' + result['title'])
        await ctx.send(message,embed=embed)
      else:
        message = "No results were found on Wikipedia."
        await ctx.send(message)


    elif 'go' in search_engine: # google search
      result = googleSearch(args)
      await ctx.send('\n'.join(result))


    elif 'ur' in search_engine: # urban dictionary search 
      result = urbanSearch(args)
      if result['response'] == 1:
        message = '**%s** \n\n%s \n\n*%s* ' % (result['word'],result['meaning'],result['example'])
        embed = discord.Embed(title=result['word'],url=result['url'],description= 'Urban Dictionary ' + result['word'])
        await ctx.send(message,embed=embed)
        
      else:
        await ctx.send('Word was not found on Urban Dictionary')


    elif 'image' in search_engine or 'img' in search_engine:
      await get_image(ctx,args,num)


    else: # google search if requsted engine is not recongised
      result = googleSearch(args)
      await ctx.send('\n'.join(result))
  except HTTPException: # google search args if error occurs
      result = googleSearch(args)
      await ctx.send('\n'.join(result))
  except Exception as err:
    exception_type = type(err).__name__
    print_log(exception_type)

  print_log('A user has requested knowleage.')


@bot.command(name='joke')
async def tell_joke(ctx):
  joke = get_joke()
  if joke['response'] == 0:
    print_log('An error has occured in the joke command')
  else:
    if joke['type'] == 'single':
      await ctx.send(joke['joke'])
    else:
      await ctx.send(joke['setup'])
      time.sleep(3)
      await ctx.send(joke['delivery'])
      print_log('A user has been entertianed')



@bot.command(name='meme')
async def meme(ctx):
  meme = await get_meme()
  await ctx.send(meme)

@bot.command(name='reddit')
async def get_random_sub_post(ctx,reddit,sort='hot'):
  response = await get_random_post(reddit,sort)
  if response['response'] == 1:
    await ctx.send('***%s***\n%s\n\n%s' % (response['title'],response['text'],response['url']))
  else:
    await ctx.send('Subreddit not found',delete_after=3)

@bot.command()
async def poll( ctx, question, *options: str):
    if len(options) <= 1:
        await ctx.send('You need more than one option to make a poll!')
        return
    if len(options) > 10:
        await ctx.send('You cannot make a poll for more than 10 things!')
        return


    if len(options) == 2 and options[0].lower() == 'yes' and options[1].lower() == 'no':
        reactions = ['✅', '❌']
    else:
        reactions = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']

    description = []
    for x, option in enumerate(options):
        description += '\n {} {}'.format(reactions[x], option)
    embed = discord.Embed(title=question, description=''.join(description))
    react_message = await ctx.send(embed=embed)
    embed.set_footer(text='Poll ID: {}'.format(react_message.id))
    await react_message.edit(embed=embed)


# The bot displays its commands
@bot.command(name='commands')
async def get_commands(ctx):
  commands = '''
  $poll 'question' *options - I will create a poll with up to 10 options
  $joke - I will tell a joke
  $meme- I will post a random meme
  $inspire - Receive a inspiring message
  $new 'quotehere' - Add a new sentence to my vocabulary
  $list - View my current vocabulary
  $del 'quoteid' - Delete a sentense from my vocabulary
  $news - Get latest news articles
  $decide choice1?choice2?choicex - I will use advanced AI technology to select the right choice for you
  $clean 'amount' - I will delete amount number of messages. Limit = 98
  $search 'engine' 'query' - I will search for whatever you tell me to on the requested engine(5 second cooldown). Default google when no engine is found
  Current engines are google, wikipedia, urban dictionary, images
  I will randomly pop in from time to time on certain comments
  '''
  response = '```' + commands + '```'
  await ctx.send(response)
  print_log('Sandbots commands have been delivered')


def print_log(message):
  sys.stdout.write(message)
  sys.stdout.flush()

async def get_image(ctx,query,num=1):
  if num == None:
    num = 1
  images = googleImage(query,num)
  for image in images:
    await ctx.send(image)
    time.sleep(1)
  print_log('A user requested images')

# @bot.command(name="startDaily")
# async def startDaily(ctx):
#   daily_word.start(ctx)

# @bot.command(name='startSales')
# async def post_sales(ctx):
#   await ctx.send('Posting latest info in this channel', delete_after=5)
#   start_sale.start(ctx)
#   print_log('Starting sale info')

# @bot.command(name='stopSales')
# async def stop_sale(ctx):
#   await ctx.send("Stopping stream",delete_after=5)
#   start_sale.cancel()
#   print_log('Sale info stopped')


