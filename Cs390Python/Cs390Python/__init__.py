"""
The flask application package.
"""

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

import Cs390Python.views
import Cs390Python.models
import Cs390Python.forms

db.create_all()