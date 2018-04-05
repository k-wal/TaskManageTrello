from flask import Blueprint
from models import User
from flask_wtf import FlaskForm
from app import db

class LoginForm(FlaskForm):
	username = StringField('username',validators=[InputRequired(), Length(max=20)])
	password = PasswordField('password',validators=[InputRequired(),Length(min=8,max=40)])
	remember=BooleanField('Remember Me')

