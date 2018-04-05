from flask import Blueprint
from models import User
from flask_wtf import FlaskForm
from app import db

user = Blueprint('user_blueprint', __name__)

@user.route('/user_registration', methods = [POST])
def register_user():
    form = RegisterForm()

    if form.validate_on_submit():
        new_user = User(username=form.username.data, name=form.name.data, dob=form.dob.data, password_hash=set_password(form.username.password))
        db.session.add(new_user)
        db.session.commit
        return '<h1>User {} has been created'.format(form.username.data)
