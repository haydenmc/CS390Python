from Cs390Python import db
from sqlalchemy import Table, Column, Integer, ForeignKey, Boolean, PrimaryKeyConstraint
from sqlalchemy.orm import relationship, backref

circle_post = db.Table('circle_post', 
                       db.Column('circle_id', db.Integer, db.ForeignKey('circle.id')),
                       db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
                       )

circle_member = db.Table('circle_member',
                         db.Column('circle_id', db.Integer, db.ForeignKey('circle.id')),
                         db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
                         )

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), index=True, unique=True)
    password = db.Column(db.String(40))
    displayName = db.Column(db.String(255))
    posts = relationship("Post", backref="author")
    joinedTime = db.Column(db.DateTime())
    verificationCode = db.Column(db.String(32))
    isVerified = db.Column(db.Boolean(), default=False)
    hasPhoto = db.Column(db.Boolean(), default=False)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<User %r>' % (self.displayName)

class Friend(db.Model):
    __tablename__ = 'friend'
    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'friend_id'),
    )
    user_id = Column(Integer, ForeignKey(User.id), primary_key=True)
    friend_id = Column(Integer, ForeignKey(User.id), primary_key=True)
    user = relationship('User', foreign_keys='Friend.user_id', backref="friends")
    friend = relationship('User', foreign_keys='Friend.friend_id', lazy='joined')

class FriendRequest(db.Model):
    __tablename__ = 'friendrequest'
    __table_args__ = (
        PrimaryKeyConstraint('sender_id', 'recipient_id'),
    )
    sender_id = Column(Integer, ForeignKey(User.id))
    recipient_id = Column(Integer, ForeignKey(User.id))
    sender = relationship('User', foreign_keys='FriendRequest.sender_id', lazy='joined')
    recipient = relationship('User', foreign_keys='FriendRequest.recipient_id', backref="incomingFriendRequests")

class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(Integer, ForeignKey('user.id'))
    body = db.Column(db.String(2048))
    postedTime = db.Column(db.DateTime())
    hasPhoto = db.Column(db.Boolean(), default=False)

class Circle(db.Model):
    __tablename__ = 'circle'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    owner_id = db.Column(Integer, ForeignKey('user.id'))
    owner = relationship('User', foreign_keys='Circle.owner_id', backref="circles")
    posts = db.relationship('Post', secondary=circle_post, backref=db.backref('circles'))
    members = db.relationship('User', secondary=circle_member, backref=db.backref('memberOfCircles'))
