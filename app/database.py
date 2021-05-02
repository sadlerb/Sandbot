import random
import sys


def getLastEntry(collection):
    last_entry = collection.find().sort([('order', -1)]).limit(1)
    return last_entry


def getRandomEntry(collection):
    lenCollection = collection.count_documents({})
    randInt = random.randint(0,lenCollection-1)
    sys.stdout.flush()
    entry = collection.find().limit(-1).skip(randInt).next()
    return entry


def getAllEntries(collection):
    entries = collection.find()
    return entries

def document_exists(collection,query,key):
    if collection.count_documents({key:query}) > 0:
        return True
    else:
        return False