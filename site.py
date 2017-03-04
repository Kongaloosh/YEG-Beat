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


def connect_db():
    return sqlite3.connect('news.db')


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.route('/')
def show_entries():
    return render_template('index.html')


if __name__ == "__main__":
    app.run()