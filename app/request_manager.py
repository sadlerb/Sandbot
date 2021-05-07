
import json
import requests
import sys
import time
from googlesearch import search
from bs4 import BeautifulSoup
from app import news_key

joke_api = 'https://v2.jokeapi.dev/'
inspiration_api = 'https://zenquotes.io/api'
news_api = 'https://newsapi.org'
wiki_api = 'https://en.wikipedia.org/w/api.php'
urban_url = 'https://www.urbandictionary.com/'
google_api = 'https://www.googleapis.com/customsearch/v1?key=AIzaSyAgJ9tfDhpTquguV7io3snS59QQUy5j--c&cx=37f70d1403a56b5a5'


def get_inspiration():
  response = requests.get( inspiration_api + '/random')
  json_data = json.loads(response.text)
  quote = json_data[0]['q'] + ' -' + json_data[0]['a']
  return (quote)


def get_news():
  news = []
  response = requests.get(news_api + '/v2/top-headlines?country=us&apiKey='+ news_key)
  json_data = json.loads(response.text)
  total = json_data['totalResults']
  for item in json_data['articles']:
    news.append({'title':item['title'],'url':item['url'],'desc':item['description'],'image':item['urlToImage']})

  return [news,total]

def wikiSearch(searchPage):
  PARAMS = {
    "action": "query",
    "format": "json",
    "list": "search",
    'utf8': 1,
    "srsearch": searchPage,
}

  response = requests.get(wiki_api,PARAMS)
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
    response_ext = requests.get(wiki_api,PARAMS_EXT)
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
  params = 'define.php?term=' + query.replace(' ','+')
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

def get_daily_urban_word():
  page = requests.get(urban_url)
  soup = BeautifulSoup(page.content,'html.parser')
  try:
    if soup.find("body",{'class':'generated'}) is not None:
      for br in soup.findAll('br'):
        br.replace_with('\n')
    word = soup.find(class_='word').text
    meaning = soup.find(class_='meaning').text
    example = soup.find(class_='example').text
    params = 'define.php?term=' + word.replace(' ','+')
    url = urban_url + params
    results = {'url':url,'word':word,'meaning':meaning,'example':example,'response':1}
    return results
  except Exception as err:
    exception_type = type(err).__name__
    print(exception_type)
    sys.stdout.flush()
    return {'response':0}

def get_joke():
  url = joke_api + 'joke/Any?blacklistFlags=racist,sexist'
  response = requests.get(url)
  json_data = json.loads(response.text)
  if json_data['error'] == True:
    return {'response': 0}
  else:
    if json_data['type'] == 'twopart':
      return {'setup': json_data['setup'],'delivery': json_data['delivery'],'type':json_data['type'],'response': 1}
    else:
      return {'joke':json_data['joke'], 'type':json_data['type'],'response':1}

def googleImage(query,num):
  images = []
  request = query.replace(' ','%20')
  url = google_api + '&q=%s&searchType=image' % (request)
  response = requests.get(url)
  json_data = json.loads(response.text)
  image = json_data['items']
  for item in range(0,num):
    images.append(image[item]['link'])
  return images
