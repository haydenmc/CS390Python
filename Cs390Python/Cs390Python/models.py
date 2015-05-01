from Cs390Python import db
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), index=True, unique=True)
    password = db.Column(db.String(40))
    displayName = db.Column(db.String(255))
    posts = relationship("Post", backref="author")
    joinedTime = db.Column(db.DateTime())

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

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(Integer, ForeignKey('user.id'))
    body = db.Column(db.String(2048))
    postedTime = db.Column(db.DateTime())