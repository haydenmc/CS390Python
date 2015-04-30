from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(Form):
    email = StringField('openid', validators=[DataRequired(message = "Please fill in all form fields"), Email(message = "You must enter a valid e-mail address")])
    password = PasswordField('password', validators=[DataRequired(message = "Please fill in all form fields"), Length(min = 4, message = "Please enter a password of at least 4 characters.")])