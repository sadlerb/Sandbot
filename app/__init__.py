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
reddit_key=os.environ['REDDIT_SECRET_KEY']
reddit_id=os.environ['REDDIT_CLIENT_ID']
reddit_password=os.environ['REDDIT_PASSWORD']
from app import main
