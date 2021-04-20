import os
import discord
import random
import pymongo
import dns
import requests
from request_manager import *
from pymongo import MongoClient
from database import *
import sys
from discord.ext import commands
import time


client = discord.Client()
client = commands.Bot(command_prefix='$')
url = os.environ['DATABASE_URL']
token = os.environ['TOKEN']
cluster = MongoClient(url)
db = cluster["DiscordDatabase"] 





sad_words = ['sad','depressed','unhappy','miserable','angry','depressing','miserable','fucked']

@client.event
async def on_ready():
  sys.stdout.write('We have logged in as {0.user}'.format(client))
  sys.stdout.flush()


@client.event
async def on_message(message):
  if message.author == client.user:
    return
  
  # The bot inspires the user with a quote upon request
  msg = message.content.lower()
  if msg.startswith('$inspire'):
    quote = get_inspiration()
    await message.channel.send(quote)
    sys.stdout.write('A user has been inspired')
    

  # If any message contains a certain word the bot responds with a message stored in the database
  if any(word in msg for word in sad_words):
    response = getRandomEntry(db['messages'])
    await message.channel.send(response['message'])
    sys.stdout.write('A user has been encouraged')

    #The users message is added to the database
  if msg.startswith('$quote'):
    collection = db["messages"]
    newMessage = msg.split('$quote ',1)[1]
    if collection.estimated_document_count() == 0:
      sys.stdout.flush()
      order = 1
    else:
      sys.stdout.flush()
      last_entry = getLastEntry(collection)
      order = last_entry[0]['order'] + 1      
    post = {'message':newMessage,'order':order}
    collection.insert_one(post)
    await message.channel.send("The Sandbot will remember that.".format(client))
    sys.stdout.write('Sandbot has remembered'.format(client))


  #The bot lists all quotes stored in the database 
  if msg.startswith('$list'):
    quoteString = ''
    quoteList = getAllEntries(db['messages'])
    for quote in quoteList:
      quoteString = quoteString + str(quote['order']) + ' )  ' + quote['message'] + '\n'

    response = "```" + quoteString + "```"
    await message.channel.send(response)
    print('The quotes have been delivered')

  if msg.startswith('$del'):
    collection = db["messages"]
    _order =  msg.split('$del ',1)[1]
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
          await message.channel.send('Quote deleted')
        else:
          await message.channel.send('That quote does not exist.')
    except ValueError:
      await message.channel.send('Please make sure the id is correct and try again.')

  #get news
  if msg.startswith('$news'):
    news_array = get_news()
    for article in news_array:
      await message.channel.send(':newspaper: | ' + article)
      time.sleep(2)
    await message.channel.send('End of articles')

  # The bot displays its commands
  if msg.startswith('$help'):
    commands = '''
    $inspire - Receive a inspiring message
    $quote 'quotehere'  - Add a new sentence to my vocabulary
    $list - View my current vocabulary
    $del <quoteID> - Delete a sentense from my vocabulary
    $news - Get latest news articles
    I will randomly pop in from time to time on certain comments
    '''
    response = '```' + commands + '```'
    await message.channel.send(response)
    print('Instructions have been delivered')
  sys.stdout.flush()


client.run(token)

