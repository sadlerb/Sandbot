import os
from pymongo.mongo_client import MongoClient
from discord.ext import commands

bot = commands.Bot(command_prefix='$')
url = os.environ['DATABASE_URL']
token = os.environ['TOKEN']
cluster = MongoClient(url)
db = cluster["DiscordDatabase"] 

from app import main
