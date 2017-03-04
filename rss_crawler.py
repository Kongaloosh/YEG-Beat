import sqlite3
import requests
import newspaper
from ConfigParser import ConfigParser
from slugify import slugify
import os
from contextlib import closing
import datetime
from newspaper.article import ArticleException

__author__ = 'kongaloosh'


config = ConfigParser()
config.read('config.ini')
DATABASE = config.get('Global', 'Database')


if not os.path.isfile("news.db"):
    with closing(sqlite3.connect(DATABASE)) as db:
        with open('schema.sql', 'r') as f:
            db.cursor().executescript(f.read())
        db.commit()

conn = sqlite3.connect(DATABASE)
c = conn.cursor()

for source in ['http://edmonton.ctvnews.ca/', 'http://globalnews.ca/edmonton/', 'http://edmontonjournal.com/']:
    print('building ' + source)
    paper = newspaper.build(source, memoize_articles=False)
    for article in paper.articles:
        try:
            article.download()
            article.parse()
            if len(article.authors) == 0:
                authors = None
            else:
                try:
                    authors = article.authors[0] + ", ".join(authors[1:])
                except IndexError:
                    authors = article.authors[0]
                except AttributeError:
                    authors = article.authors[0]
                except TypeError:
                    authors = article.authors[0]

            title = article.title
            published = article.publish_date
            if published is None:
                published = datetime.datetime.now()
            slug = slugify(title)
            try:
                image = article.images[0]
            except IndexError:
                image = None
            article.nlp()
            summary = article.summary
            keywords = article.keywords
            url = article.url
            location = None

            """
                create table articles (
                  id integer primary key autoincrement,
                  slug text not null,
                  summary text not null,
                  author text,
                  url text not null,
                  image text,
                  published date not null,
                  location text,
                );
            """

            c.execute(
                """
                    insert into articles
                    (slug, summary, author, url, image, published, location) values (?,?,?,?,?,?,?)
                """,
                [slug, summary, authors, url, image, published, location]
            )

            """
            create table categories(
              id integer primary key autoincrement,
              slug text not null,
              published date not null,
              category text not null,
              FOREIGN KEY (slug) REFERENCES articles(slug)
            );
            """
            conn.commit()
            for key in keywords:
                c.execute(
                    """
                        insert into categories (slug, published, category) values (?,?,?)
                    """,
                    [slug, published, key]
                )
                conn.commit()
        except ArticleException:
            print("ARTICLE EXCEPTION")