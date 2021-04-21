import os
import sys
import time
from datetime import datetime
from app import db, bot
from app.database import document_exists, getAllEntries, getLastEntry, getRandomEntry
from app.request_manager import get_inspiration, get_news







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
  sys.stdout.write('A user has been inspired')
  sys.stdout.flush()
    

  #The users message is added to the database
@bot.command(name='new')
async def save_quote(ctx,arg):
  collection = db["messages"]
  newMessage = arg

  if collection.estimated_document_count() == 0:
    order = 1
  else:
    last_entry = getLastEntry(collection)
    order = last_entry[0]['order'] + 1    

  post = {'message':newMessage,'order':order}
  collection.insert_one(post)
  await ctx.send('The Sandbot will remember that')
  sys.stdout.write('Sandbot has remembered')
  sys.stdout.flush()

  #The bot lists all quotes stored in the database 
@bot.command(name='list')
async def getlist(ctx):
  quoteString = ''
  quoteList = getAllEntries(db['messages'])
  for quote in quoteList:
    quoteString = quoteString + str(quote['order']) + ' )  ' + quote['message'] + '\n'

  response = "```" + quoteString + "```"
  await ctx.send(response)
  print('The quotes have been delivered')
  sys.stdout.flush()

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
          await ctx.send('Quote deleted')
          sys.stdout.write('Quote deleted')
        else:
          await ctx.send('That quote does not exist.')
          sys.stdout.write('The requested quote was not found')
  except ValueError:
    await ctx.send('Please make sure the id is correct and try again.')
  sys.stdout.flush()
#get news
@bot.command()
async def news(ctx):
  news_array = get_news()
  now = datetime.now().strftime('%d-%m-%Y at %H:%M')
  await ctx.send('Beginning of articles for ' + now )
  for article in news_array:
    time.sleep(2)
    await ctx.send('\n ' + ':newspaper: | ' + article)

  await ctx.send('End of articles')
  sys.stdout.write('News has been delivered at ' + now )
  sys.stdout.flush()
# The bot displays its commands
@bot.command(name='commands')
async def get_commands(ctx):
  commands = '''
  $inspire - Receive a inspiring message
  $quote 'quotehere'  - Add a new sentence to my vocabulary
  $list - View my current vocabulary
  $del <quoteID> - Delete a sentense from my vocabulary
  $news - Get latest news articles
  I will randomly pop in from time to time on certain comments
  '''
  response = '```' + commands + '```'
  await ctx.send(response)
  print('Instructions have been delivered')
sys.stdout.flush()




