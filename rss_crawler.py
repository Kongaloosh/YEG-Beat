import requests
import newspaper
from slugify import slugify



__author__ = 'kongaloosh'



ctv_url = 'http://edmonton.ctvnews.ca/'
print("building CTV")
ctv = newspaper.build(ctv_url, memoize_articles=False)
print(ctv)
for category in ctv.category_urls():
    print(category)

for article in ctv.articles:
    article.download()