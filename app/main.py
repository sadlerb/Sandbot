import os
import sys
import time
import random
from datetime import datetime
from app import db, bot
from app.database import document_exists, getAllEntries, getLastEntry, getRandomEntry
from app.request_manager import get_inspiration, get_news
from discord.ext.commands.errors import MissingRequiredArgument
import asyncio







sad_words = ['sad','depressed','unhappy','miserable','angry','depressing','miserable','fucked']

@bot.event
async def on_ready():
  sys.stdout.write('We have logged in as {0.user}'.format(bot))
  sys.stdout.flush()

@bot.event
async def on_message(message):
  if message.author == bot.user:
    return

  if any(word in message.content for word in sad_words):
    response = getRandomEntry(db['messages'])
    await message.channel.send(response['message'])
    sys.stdout.write('A user has been encouraged')
    sys.stdout.flush()
  await bot.process_commands(message)


# The bot inspires the user with a quote upon request
@bot.command()
async def inspire(ctx):
  quote = get_inspiration()
  await ctx.send(quote)
  print_log('A user has been inspired')
    
@bot.event
async def on_message_edit(before,after):
  if before.author == bot.user:
    return
  await after.channel.send('I saw that edit '  + after.author.name + '.')
  print_log('A user has been warned')
  #The users message is added to the database
@bot.command(name='new')
async def save_quote(ctx, *, arg):
  collection = db["messages"]
  newMessage = arg.strip()
  if collection.estimated_document_count() == 0:
    order = 1
  else:
    last_entry = getLastEntry(collection)
    order = last_entry[0]['order'] + 1    

  post = {'message':newMessage,'order':order}
  collection.insert_one(post)
  await ctx.send('The Sandbot will remember that',delete_after=5)
  print_log('Sandbot has remembered')

  #The bot lists all quotes stored in the database 
@bot.command(name='list')
async def getlist(ctx):
  quoteString = ''
  quoteList = getAllEntries(db['messages'])
  for quote in quoteList:
    quoteString = quoteString + str(quote['order']) + ' )  ' + quote['message'] + '\n'

  response = "```" + quoteString + "```"
  await ctx.send(response)
  print_log('The quotes have been delivered')

@bot.command(name='del')
async def delete(ctx,arg):
  collection = db["messages"]
  _order =  arg
  try:
      order = int(_order)
      if document_exists(collection,order,'order') :
        quoteList = collection.find().skip(order-1)
        if order <= collection.count_documents({}) :
          results = collection.delete_one({"order":order})
          sys.stdout.flush()
          for x in quoteList:
            query = { "order": x['order'] }
            newvalues = { "$set": { "order": x['order'] - 1 }}
            collection.update_one(query,newvalues)
            sys.stdout.flush()
          await ctx.send('Quote deleted',delete_after=5)
          sys.stdout.write('Quote deleted')
        else:
          await ctx.send('That quote does not exist.')
          sys.stdout.write('The requested quote was not found',delete_after=5)
  except ValueError:
    await ctx.send('Please make sure the id is correct and try again.',delete_after=5)
  except MissingRequiredArgument:
    await ctx.send('Please insert the number of the quote you want deleted',delete_after=5)
  sys.stdout.flush()
#get news
@bot.command()
async def news(ctx):
  response = get_news()
  news_array = response[0]
  number = response[1]
  now = datetime.now().strftime('%d-%m-%Y at %H:%M')
  await ctx.send('Beginning of articles for ' + now )
  for article in news_array:
    time.sleep(2)
    await ctx.send('\n ' + ':newspaper: | ' + article)

  await ctx.send( str(number) + ' articles sent at ' + now)
  print_log('News has been delivered')

@bot.command()
async def decide(ctx, *, args):
  choices = args.split('?')
  await ctx.send('Sandbot thinks you should ' + random.choice(choices))
  print_log('Sandbot made a very difficult decision')

@bot.command()
async def clean(ctx,amount):
  mgs = []
  if amount is None:
    await ctx.channel.send('Please enter the number of messages you want deleted',delete_after=5)
  else:
    amount = int(amount)
    if amount > 98 or amount < 1:
      await ctx.send('Please enter a number between 1 and 98',delete_after=5)
      return 
    await ctx.send('Add reaction 👍 to confirm',delete_after=10)

    def check (reaction,user):
      return user == ctx.message.author and str(reaction.emoji) == '👍'

    try:
      reaction,user = await bot.wait_for('reaction_add',timeout=10,check=check)
    except ValueError:
      ctx.channel.send('Please enter a number',delete_after=5)
    except asyncio.TimeoutError:
      await ctx.send('Method aborted',delete_after=5)
    else:
      async for m in ctx.channel.history(limit=amount+2):
        mgs.append(m)
      await ctx.channel.delete_messages(mgs)
      await ctx.send('The evidence has been removed',delete_after=5)
      print_log('Some evidence was removed')



# The bot displays its commands
@bot.command(name='commands')
async def get_commands(ctx):
  commands = '''
  $inspire - Receive a inspiring message
  $new 'quotehere'  - Add a new sentence to my vocabulary
  $list - View my current vocabulary
  $del 'quoteid' - Delete a sentense from my vocabulary
  $news - Get latest news articles
  $decide choice1?choice2?choicex - I will use advanced AI technology to select the right choice for you
  $clean 'amount'- I will delete amount number of messages. Limit = 98
  I will randomly pop in from time to time on certain comments
  '''
  response = '```' + commands + '```'
  await ctx.send(response)
  print_log('Instructions have been delivered')

def print_log(message):
  sys.stdout.write(message)
  sys.stdout.flush()

