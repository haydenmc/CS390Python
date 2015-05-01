"""
The flask application package.
"""

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
import os

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(APP_ROOT, 'uploads')

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

import Cs390Python.views
import Cs390Python.models
import Cs390Python.forms

db.create_all()