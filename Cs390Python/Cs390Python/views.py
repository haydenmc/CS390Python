"""
Routes and views for the flask application.
"""

import os
import base64
from datetime import datetime
from flask import render_template, flash, redirect, g, url_for, request, send_from_directory
from flask.ext.login import login_user, logout_user, current_user, login_required
from Cs390Python import app, lm, db
from Cs390Python.forms import LoginForm, RegisterForm, NewPostForm, UserSearchForm, ProfilePhotoForm, NameInfoForm, EmailPassForm
from Cs390Python.models import User, Post, Friend, FriendRequest
from sqlalchemy import desc
from werkzeug import secure_filename
import sendgrid

@app.before_request
def before_request():
    g.user = current_user
    g.year = datetime.now().year

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
        userSearchForm=userSearchForm,
        results=results
        )

@app.route('/me', methods=['GET', 'POST'])
@login_required
def me():
    profileUser=User.query.filter_by(id = g.user.id).first()
    profilePhotoForm=ProfilePhotoForm()
    nameInfoForm=NameInfoForm()
    emailPassForm=EmailPassForm()
    if profilePhotoForm.validate_on_submit():
        filename = secure_filename(profilePhotoForm.photo.data.filename)
        profilePhotoForm.photo.data.save(os.path.join(app.config['UPLOAD_FOLDER'], "avatars", str(g.user.id) + ".jpg"))
        profileUser.hasPhoto = True
        db.session.commit()
        flash('Your profile photo has been updated.')
    else:
        filename = None
    if nameInfoForm.validate_on_submit():
        profileUser.displayName = nameInfoForm.name.data
        db.session.commit()
        flash('Your name has been changed.')
    if emailPassForm.validate_on_submit():
        profileUser.email = emailPassForm.email.data
        profileUser.password = emailPassForm.password.data
        flash('Your email and password have been set.')
    return render_template(
        'me.html',
        title=g.user.displayName,
        profilePhotoForm=profilePhotoForm,
        nameInfoForm=nameInfoForm,
        emailPassForm=emailPassForm
        )

@app.route('/avatar/<userid>')
@login_required
def avatar(userid):
    user=User.query.filter_by(id=userid).first()
    if user.hasPhoto:
        return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], "avatars"), str(g.user.id) + ".jpg")
    else:
        return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], "avatars"), "0.jpg")

@app.route('/profile/<userid>')
@login_required
def profile(userid):
    profileUser=User.query.filter_by(id = userid).first()
    return render_template(
        'profile.html',
        title=profileUser.displayName + "'s Profile",
        profileUser=profileUser
        )

@app.route('/addfriend/<userid>')
@login_required
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
@login_required
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Renders the login page."""
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('home'))
    form=LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data, password = form.password.data).first()
        if user is None:
            flash('Invalid credentials. Please try again.')
            return redirect(url_for('login'))
        if not user.isVerified:
            flash('This account has not yet been activated.')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(request.args.get('next') or url_for('home'))
    return render_template(
        'login.html',
        title='Sign In',
        form=form,
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
        random_string = base64.urlsafe_b64encode(os.urandom(32)).decode('ascii')
        user = User(email=form.email.data, password=form.password.data, displayName=form.displayName.data, verificationCode=random_string)
        user.isVerified = True # Remove for demo
        db.session.add(user)
        db.session.commit()
        #sg = sendgrid.SendGridClient("mylink", "cs390python")
        #message = sendgrid.Mail()
        #message.add_to(user.email)
        #message.set_from("MyLink <admin@mylink.purdue.io>")
        #message.set_subject("Please verify your account")
        #message.set_text("Hello! Thank you for registering with MyLink.\nPlease click the link below to activate your account.\nhttp://mylink.purdue.io/verify/" + random_string)
        #sg.send(message)
        flash('Account created successfully. Please check your e-mail to verify the account before logging in.')
        return redirect(url_for('login'))
    return render_template(
        'register.html',
        title='Register',
        form=form,
        )

@app.route('/verify/<verificationCode>')
def verify(verificationCode):
    user = User.query.filter_by(verificationCode=verificationCode).first()
    if (user is None):
        flash("Verification code is no longer valid.")
        return redirect(url_for('login'))
    user.isVerified = True
    user.verificationCode = ""
    db.session.commit()
    flash("Your account has been verified. Please log in.")
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))