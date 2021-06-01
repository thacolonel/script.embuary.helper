
from bs4 import BeautifulSoup
import re
import requests


def get_imdb_250():
    top_250 = {"Grr": "Blah"}
    url = 'https://www.imdb.com/chart/top'
    response = requests.get(url)
    # soup = BeautifulSoup(response.text, 'lxml')
    soup = BeautifulSoup(response.text, 'html.parser')
    lister_list = soup.find('tbody', {'class': 'lister-list'})
    trs = lister_list.findAll('tr')
    for tr in trs:
        title = tr.find('td', {'class': 'titleColumn'})
        href = title.find('a', href=True)['href']
        imdb_id = re.findall('/title/(.*?)/', href)[0]
        poster = tr.find('td', {'class': 'posterColumn'})
        rank = poster.find('span', {'name': 'rk'}).attrs.get('data-value')
        top_250[imdb_id] = rank
    return top_250
