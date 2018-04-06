from flask import Blueprint, render_template, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.fields.html5 import DateField
from wtforms.validators import Email, EqualTo, Length, Required, InputRequired
from models import db, User


user_blueprint = Blueprint('user_blueprint', __name__)


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
                           InputRequired(), Length(max=32)])
    password = PasswordField('Password', validators=[
                             Required(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Retype Password', validators=[
                            Required(), Length(min=8, max=80)])
    dob = DateField('Date Of Birth', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    name = StringField('Name', validators=[InputRequired(), Length(max=64)])


class LoginForm(FlaskForm):
    username = StringField('username', validators=[
                           InputRequired(), Length(max=20)])
    password = PasswordField('password', validators=[
                             InputRequired(), Length(min=8, max=40)])
    remember = BooleanField('Remember Me')


@user_blueprint.route('/user/registration', methods=['POST', 'GET'])
def register_user():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, name=form.name.data,
                        dob=form.dob.data, password_hash=User.hash_password(form.password.data))
        db.session.add(new_user)
        db.session.commit()
        return '<h1>{} has been created!</h1>'.format(new_user.username)
    return render_template('register.html', form=form)


@user_blueprint.route('/user/login', methods=['POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            return '<h1>Invalid username or password</h1>'
            # return redirect(url_for('login'))

        login_user(user, remember=form.remember.data)
        return '<h1>Login Successful</h1>'
        # return redirect(url_for('index'))
    return render_template('login.html', form=form)
