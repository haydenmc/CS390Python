"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, flash, redirect, g, url_for, request
from flask.ext.login import login_user, logout_user, current_user, login_required
from Cs390Python import app, lm, db
from Cs390Python.forms import LoginForm, RegisterForm, NewPostForm
from Cs390Python.models import User, Post
from sqlalchemy import desc

@app.before_request
def before_request():
    g.user = current_user

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    """Renders the home page."""
    form=NewPostForm()
    if form.validate_on_submit():
        newPost = Post(body=form.body.data, author=g.user, postedTime = datetime.now())
        db.session.add(newPost)
        db.session.commit()
        flash('New post added!')
    posts=Post.query.order_by('postedTime desc').all()
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
        postForm=form,
        posts=posts
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
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('home'))
    form=LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data, password = form.password.data).first()
        if user is None:
            flash('Invalid credentials. Please try again.');
            return redirect(url_for('login'));
        login_user(user)
        return redirect(request.args.get('next') or url_for('home'))
    return render_template(
        'login.html',
        title='Sign In',
        form=form,
        year=datetime.now().year
        )

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Renders the register page."""
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('home'))
    form=RegisterForm()
    if form.validate_on_submit():
        # Check if user exists...
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            flash('This e-mail address is already in use.');
            return redirect(url_for('register'))
        user = User(email=form.email.data, password=form.password.data, displayName=form.displayName.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully. You may now log in.')
        return redirect(url_for('login'))
    return render_template(
        'register.html',
        title='Register',
        form=form,
        year=datetime.now().year)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))