"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, flash, redirect, g, url_for, request
from flask.ext.login import login_user, logout_user, current_user, login_required
from Cs390Python import app, lm, db
from Cs390Python.forms import LoginForm, RegisterForm, NewPostForm, UserSearchForm
from Cs390Python.models import User, Post, Friend, FriendRequest
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

@app.route('/friends')
@login_required
def friends(): 
    """Renders the friend list."""
    dbUser = User.query.filter_by(id = g.user.id).first()
    friends = dbUser.friends
    friendRequests = dbUser.incomingFriendRequests
    return render_template(
        'friends.html',
        title='Friends',
        year=datetime.now().year,
        friends=friends,
        friendRequests=friendRequests
        )

@app.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    """Allows searching for users"""
    userSearchForm=UserSearchForm()
    results=None
    if userSearchForm.validate_on_submit():
        results = User.query.filter(User.displayName.like("%" + userSearchForm.name.data + "%")).all()
        if results is None:
            flash('Could not find any users matching your search.');
    return render_template(
        'users.html',
        title='Users',
        year=datetime.now().year,
        userSearchForm=userSearchForm,
        results=results
        )

@app.route('/profile/<userid>')
def profile(userid):
    profileUser=User.query.filter_by(id = userid).first()
    return render_template(
        'profile.html',
        title=profileUser.displayName + "'s Profile",
        profileUser=profileUser
        )

@app.route('/addfriend/<userid>')
def addfriend(userid):
    addedUser=User.query.filter_by(id = userid).first()
    check=FriendRequest.query.filter_by(sender_id=g.user.id, recipient_id=addedUser.id).first()
    if check is not None:
        flash("You have already sent a friend request to this user.")
        return redirect(url_for('profile',userid=userid))
    newRequest=FriendRequest(sender_id=g.user.id, recipient_id=addedUser.id)
    db.session.add(newRequest)
    db.session.commit()
    flash("Your friend request has been sent.");
    return redirect(url_for('friends'))

@app.route('/acceptfriend/<userid>')
def acceptfriend(userid):
    request=FriendRequest.query.filter_by(sender_id=userid, recipient_id=g.user.id).first()
    if request is None:
        flash("This user has not sent you a request.")
        return redirect(url_for('profile', userid=userid))
    friendOne=Friend(user_id=request.recipient_id, friend_id=request.sender_id)
    friendTwo=Friend(user_id=request.sender_id, friend_id=request.recipient_id)
    db.session.add(friendOne)
    db.session.add(friendTwo)
    db.session.delete(request)
    db.session.commit()
    flash(request.sender.displayName + " has been added as your friend.")
    return redirect(url_for('friends'))

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