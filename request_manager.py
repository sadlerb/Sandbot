
import json
import requests
import sys


def get_inspiration():
  response = requests.get('https://zenquotes.io/api/random')
  json_data = json.loads(response.text)
  quote = json_data[0]['q'] + ' -' + json_data[0]['a']
  return (quote)


def get_news():
  news = []
  response = requests.get('https://newsapi.org/v2/top-headlines?country=us&apiKey=9e638516f05e48f28b85bd65158e59c7')
  json_data = json.loads(response.text)
  for item in json_data['articles']:
    news.append('\n' + '**' + item['title'] + '**' + '\n' + '\n' + item['urlToImage'] +'\n')
  return news