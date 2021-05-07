import os
from pymongo.mongo_client import MongoClient
from discord.ext import commands

bot = commands.Bot(command_prefix='$')
url = os.environ['DATABASE_URL']
token = os.environ['TOKEN']
cluster = MongoClient(url)
db = cluster["DiscordDatabase"] 
news_key = os.environ['NEWS_KEY']
google_key = os.environ['GOOGLE_KEY']
engine_id = os.environ['SEARCH_ID']
from app import main
