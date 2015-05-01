from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class LoginForm(Form):
    email = StringField('email', validators=[DataRequired(message = "Please fill in all form fields"), Email(message = "You must enter a valid e-mail address")])
    password = PasswordField('password', validators=[DataRequired(message = "Please fill in all form fields"), Length(min = 4, message = "Please enter a password of at least 4 characters.")])

class RegisterForm(Form):
    email = StringField('email', validators=[DataRequired(message = "Please fill in all form fields"), Email(message = "Please enter a valid e-mail address")])
    displayName = StringField('displayName', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired(), Length(min = 4, message = "Please enter a password of at least 4 characters.")])
    confirmPassword = StringField('confirmPassword', validators=[DataRequired(), EqualTo('password', "Your passwords do not match.")])

class NewPostForm(Form):
    body = StringField('body', validators=[DataRequired(message = "Please type a message to post")])