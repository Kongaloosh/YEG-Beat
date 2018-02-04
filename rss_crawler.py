"""
A crawler to pull news articles


"""

import sqlite3
import requests
import newspaper as newspaper
from configparser import ConfigParser
from slugify import slugify
import os
from contextlib import closing
import datetime
from newspaper.article import ArticleException
from nltk import word_tokenize, pos_tag, ne_chunk, sent_tokenize, ne_chunk_sents

__author__ = 'kongaloosh'


config = ConfigParser()
config.read('config.ini')
DATABASE = config.get('Global', 'Database')


if not os.path.isfile(DATABASE):                    # if the db does not exist
    with closing(sqlite3.connect(DATABASE)) as db:  # open db
        with open('schema.sql', 'r') as f:          # read the schema
            db.cursor().executescript(f.read())     # execute the schema to make the db
        db.commit()

conn = sqlite3.connect(DATABASE)
c = conn.cursor()



def extract_entity_names(t):
    entity_names = []

    if hasattr(t, 'label') and t.label:
        if t.label() == 'NE':
            entity_names.append(' '.join([child[0].title() for child in t]))
        else:
            for child in t:
                entity_names.extend(extract_entity_names(child))

    return entity_names


def entity_extractor(sentence):
    sentences = sent_tokenize(sentence)
    tokenized_sentences = [word_tokenize(sentence) for sentence in sentences]
    tagged_sentences = [pos_tag(sentence) for sentence in tokenized_sentences]
    chunked_sentences = ne_chunk_sents(tagged_sentences, binary=True)

    entity_names = []
    for tree in chunked_sentences:
        # Print results per sentence
        # print extract_entity_names(tree)

        entity_names.extend(extract_entity_names(tree))
    return entity_names

for source in ['https://foreignpolicy.com/', 'https://www.ft.com/', 'https://www.aljazeera.com/', 'https://www.cnn.com/']:
    print('building ' + source)
    paper = newspaper.build(source, memoize_articles=False)
    for article in paper.articles:
        authors = None
        try:
            article.download()
            article.parse()
            if len(article.authors) > 0:
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
            if title:
                slug = slugify(title)
            else:
                slug = article.summary[:10]
            try:
                image = article.images.pop()
            except IndexError:
                image = None
            article.nlp()
            summary = article.summary
            if len(summary) < 50:
                break
            keywords = entity_extractor(article.text)
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
