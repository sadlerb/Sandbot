
import json
import requests
import sys
import time
from googlesearch import search
from bs4 import BeautifulSoup


inspiration_url = 'https://zenquotes.io/api'
news_url = 'https://newsapi.org'
wiki_url = 'https://en.wikipedia.org/w/api.php'
urban_url = 'https://www.urbandictionary.com/define.php'



def get_inspiration():
  response = requests.get( inspiration_url + '/random')
  json_data = json.loads(response.text)
  quote = json_data[0]['q'] + ' -' + json_data[0]['a']
  return (quote)


def get_news():
  news = []
  response = requests.get(news_url + '/v2/top-headlines?country=us&apiKey=9e638516f05e48f28b85bd65158e59c7')
  json_data = json.loads(response.text)
  total = json_data['totalResults']
  for item in json_data['articles']:
    sys.stdout.flush()
    news.append('**' + item['title'] + '**' +  '\n >>> ' + item['url'] + '\n')
  return [news,total]

def wikiSearch(searchPage):
  PARAMS = {
    "action": "query",
    "format": "json",
    "list": "search",
    'utf8': 1,
    "srsearch": searchPage,
}

  response = requests.get(wiki_url,PARAMS)
  json_data = json.loads(response.text.encode('utf-8').decode('ascii', 'ignore'))
  if json_data['query']['searchinfo']['totalhits'] != 0:
    page = json_data['query']['search'][0]
    PARAMS_EXT = {
    "action": "query",
    "format": "json",
    "pageids": page['pageid'],
    'utf8': 1,
    'prop': 'extracts',
    'exsentences': 3,
    'explaintext': 1
}
    time.sleep(1)
    response_ext = requests.get(wiki_url,PARAMS_EXT)
    json_data = json.loads(response_ext.text.encode('utf-8').decode('ascii', 'ignore'))
    extract = json_data['query']['pages'][str(page['pageid'])]['extract']
    url = 'https://en.wikipedia.org/wiki/' + page['title'].replace(' ','_')
    result = {
      'response': 1,
      'title':page['title'],
      'extract': extract,
      'url' : url
    }
  else:
    result = {'response': 0}
  return result



def googleSearch(query):
  results= []
  for j in search(query, tld="co.in", num=3, stop=3, pause=1):
    results.append(j)
  return results

def urbanSearch(query):
  params = '?term=' + query.replace(' ','+')
  url = urban_url + params
  page = requests.get(url)
  soup = BeautifulSoup(page.content,'html.parser')
  if soup.find("body", {"class": "generated"}) is not None:
    for br in soup.findAll('br'):
      br.replace_with('\n')
    word = soup.find(class_='word').text
    meaning = soup.find(class_='meaning').text
    example = soup.find(class_='example').text
    results = {'url':url,'word':word,'meaning':meaning,'example':example,'response':1}
  else:
    results = {'response':0}
  return results