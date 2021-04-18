import os
import discord
import random
import pymongo
import dns
import requests
from helpers import get_quote
from pymongo import MongoClient
from database import *
import sys


client = discord.Client()
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
  msg = message.content
  if msg.startswith('$inspire'):
    quote = get_quote()
    await message.channel.send(quote)
    sys.stdout.write('A user has been inspired')
    

  # If any message contains a certain word the bot responds with a message stored in the database
  if any(word in msg for word in sad_words):
    response = getRandomEntry(db['messages'])
    await message.channel.send(response['message'])
    sys.stdout.write('A user has been encouraged')

    #The users message is added to the database
  if msg.startswith('$new'):
    collection = db["messages"]
    newMessage = msg.split('$new ',1)[1]
    if collection.estimated_document_count() == 0:
      sys.stdout.flush()
      order = 1
    else:
      sys.stdout.flush()
      last_entry = getLastEntry(collection)
      order = last_entry[0]['order'] + 1      
    post = {'message':newMessage,'order':order}
    collection.insert_one(post)
    await message.channel.send("The Degenerate will remember that.")
    sys.stdout.write('The Degenerate has remembered')


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
      results = collection.delete_one({"order":order})
      if not document_exists(collection,order,'order') :
        quoteList = collection.find().skip(order-1)
        if order <= quoteList.count():
          for x in quoteList:
            query = { "order": x['order'] }
            newvalues = { "$set": { "order": x['order'] - 1 }}
            collection.update_one(query,newvalues)
            print(x)
            sys.stdout.flush()
          await message.channel.send('Quote deleted')
        else:
          await message.channel.send('That quote does not exist.')
    except ValueError:
      await message.channel.send('Please make sure the id is correct and try again.')

  # The bot displays its commands
  if msg.startswith('$help'):
    commands = '''
    $inspire - Receive a inspiring message
    $new <quote>  - Add a new sentence to my vocabulary
    $list - View my current vocabulary
    $del <quoteID> - Delete a sentense from my vocabulary
    I will randomly pop in from time to time on certain comments
    '''
    response = '```' + commands + '```'
    await message.channel.send(response)
    print('Instructions have been delivered')
  sys.stdout.flush()

client.run(token)

