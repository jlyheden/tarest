from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
# :memory:
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
DB_PATH = os.getenv("DB_PATH", "")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://{}'.format(DB_PATH)
db = SQLAlchemy(app)

import tarest.domain
import tarest.api


def init_db():
    db.create_all()


init_db()
