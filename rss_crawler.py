import sqlite3
import requests
import newspaper
from ConfigParser import ConfigParser

__author__ = 'kongaloosh'

config = ConfigParser()
config.read('config.ini')

DATABASE = config.get('Global', 'Database')
conn = sqlite3.connect(DATABASE)
c = conn.cursor()

ctv_url = 'http://edmonton.ctvnews.ca/'
print("building CTV")
ctv = newspaper.build(ctv_url, memoize_articles=False)
print(ctv)
for category in ctv.category_urls():
    print(category)

for article in ctv.articles:
    article.download()