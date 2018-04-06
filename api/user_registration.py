from flask import Blueprint, render_template, url_for, request
from models import User
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Length, EqualTo
from models import db, User


user_blueprint = Blueprint('user_blueprint', __name__)


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
                           InputRequired(), Length(max=32)])
    name = StringField('Name', validators=[InputRequired(), Length(max=64)])
    dob = DateField('Date Of Birth', validators=[InputRequired()])
    password = PasswordField('Password', validators=[
                             InputRequired(), Length(min=8, max=80), EqualTo('confirm')])
    confirm = PasswordField('Confirm Password', validators=[
                            InputRequired(), Length(min=8, max=80)])


class LoginForm(FlaskForm):
    username = StringField('username', validators=[
                           InputRequired(), Length(max=20)])
    password = PasswordField('password', validators=[
                             InputRequired(), Length(min=8, max=40)])
    remember = BooleanField('Remember Me')


@user_blueprint.route('/user/registration', methods=['POST', 'GET'])
def register_user():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        new_user = User(username=form.username.data, name=form.name.data,
                        dob=form.dob.data, password_hash=set_password(form.username.password))
        db.session.add(new_user)
        db.session.commit
        return render_template('/templates/register.html', form=form)

    return '<h1>Oops.</h1><br><h2>Some error occured, please try again later.</h2>'


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
