"""
The flask application package.
"""

from flask import Flask
app = Flask(__name__)
app.config.from_pyfile('config.py')

import Cs390Python.views
import Cs390Python.forms