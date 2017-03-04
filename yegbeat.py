from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, Response
import sqlite3
from contextlib import closing
import os
from ConfigParser import ConfigParser

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
            LIMIT 10
        """
    )
    for (id, slug, summary, author, url, image, published, location) in cur.fetchall():
        try:
            if len(author) > 25:
                author = None
        except TypeError:
            pass

        articles.append({
            'id':id,
            'slug':slug,
            'summary':summary,
            'author':author,
            'url':url,
            'image':image,
            'published':published,
            'location':location
        })



        for article in articles:
            print(article['slug'])
            cur = g.db.execute(
                """
                    SELECT category FROM categories
                    WHERE categories.slug = '{0}'
                """.format(article['slug'])
            )
            categories = [str(i) for i in cur.fetchall()]

            article['category'] = categories

    return render_template('index.html', articles=articles)


@app.route('/t/<category>')
def tag_search(category):
    """ Get all entries with a specific tag """
    entries = []
    cur = g.db.execute(
        """
         SELECT entry.title FROM categories
         INNER JOIN entries ON
         entries.slug = categories.slug AND
         entries.published = categories.published
         WHERE categories.category='{category}'
         ORDER BY entries.published DESC
        """.format(category=category))
    for (row,) in cur.fetchall():
        if os.path.exists(row + ".json"):
            entries.append(file_parser_json(row + ".json"))
    return render_template('blog_entries.html', entries=entries)



if __name__ == "__main__":
    if not os.path.isfile("news.db"):
        init_db()
    app.run()
    # app.run(host='127.0.0.1', port=1000)