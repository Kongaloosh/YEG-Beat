from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, Response
import sqlite3
from contextlib import closing
import os
from configparser import ConfigParser

__author__ = 'kongaloosh'

config = ConfigParser()
config.read('config.ini')

DATABASE = config.get('Global', 'Database')
DEBUG = config.get('Global', 'Debug')
SECRET_KEY = config.get('Global', 'DevKey')
USERNAME = config.get('SiteAuthentication', "Username")
PASSWORD = config.get('SiteAuthentication', 'password')
DOMAIN_NAME = config.get('Global', 'DomainName')
GEONAMES = config.get('GeoNamesUsername', 'Username')
FULLNAME = config.get('PersonalInfo', 'FullName')

print(DATABASE, USERNAME, PASSWORD, DOMAIN_NAME)


# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config['STATIC_FOLDER'] = os.getcwd()
cfg = None

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/')
def show_entries():
    articles = []
    cur = g.db.execute(
        """
            SELECT * FROM articles
            ORDER BY articles.published DESC
        """
    )
    for (id, slug, summary, author, url, image, published, location) in cur.fetchall():
        try:
            if len(author) > 25:
                author = None
        except TypeError:
            pass
        
        articles.append({
            'id': id,
            'slug': slug,
            'summary': summary,
            'author': author,
            'url': url,
            'image': image,
            'published': published,
            'location': location
        })

    try:
        articles = articles[:10]
    except IndexError:
        pass

    cur = g.db.execute(
        """
            SELECT  categories.category
            FROM categories
            INNER JOIN articles on articles.slug == categories.slug
            WHERE date(articles.published) BETWEEN date('now','-2 day') AND date('now')
            GROUP BY categories.category
            ORDER BY COUNT(categories.category) DESC
            LIMIT 40
        """
    )

    categories = cur.fetchall()

    articles = []
    for category in categories:
        cur = g.db.execute(
            """ 
            SELECT distinct(articles.id), 
            articles.slug, 
            articles.summary, 
            articles.author, 
            articles.url, 
            articles.image, 
            articles.published, 
            articles.location
            FROM articles
            INNER JOIN categories on articles.slug == categories.slug
            WHERE date(articles.published) BETWEEN date('now','-2 day') AND date('now')
            AND categories.category='{0}'
            """.format(category[0])
        )
        entries = []
        #
        # e = cur.fetchall()
        # print(len(e[0]))

        for (id, slug, summary, author, url, image, published, location) in cur.fetchall():
            try:
                if len(author) > 25:
                    author = None
            except TypeError:
                pass

            a = {
                'id': id,
                'slug': slug,
                'summary': summary,
                'author': author,
                'url': url,
                'image': image,
                'published': published,
                'location': location
            }
            if summary=='' or slug=='':
                break
            entries.append(a)
        articles.append((category[0], entries))

    return render_template('index.html', articles=articles)


if __name__ == "__main__":
    if not os.path.isfile("news.db"):
        init_db()
    app.run()