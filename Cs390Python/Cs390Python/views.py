"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, flash, redirect
from Cs390Python import app
from Cs390Python import forms
from Cs390Python.forms import LoginForm

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Renders the login page."""
    form=LoginForm()
    if form.validate_on_submit():
        flash('ding dong')
        return redirect('/')
    return render_template(
        'login.html',
        title='Sign In',
        form=form
        )