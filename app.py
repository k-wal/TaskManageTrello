from flask import Flask, Blueprint, render_template, url_for, request, redirect, flash
from config.config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from api.user_registration import user_blueprint
from api.add_task import task_blueprint
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.fields.html5 import DateField
from wtforms.validators import Email, EqualTo, Length, Required, InputRequired
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import db, User

app = Flask(__name__)
app.config.from_object(Config)
# db = SQLAlchemy(app)
# migrate = Migrate(app, db)

#NEED TO FIND OUT HOW @login_required for blueprints
# app.register_blueprint(user_blueprint)
app.register_blueprint(task_blueprint)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


### FROM api.user_registration
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

    
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(max=32)])
    password = PasswordField('Password', validators=[Required(), EqualTo('confirm', message='Passwords must match')])
    confirm  = PasswordField('Retype Password', validators=[Required(),Length(min=8, max=80)])
    dob = DateField('Date Of Birth', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    name = StringField('Name', validators=[InputRequired(), Length(max=64)])

@app.route('/user/registration', methods = ['POST', 'GET'])
def register_user():

    if current_user.is_authenticated:
        return redirect("/"+current_user.username+"/home")

    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method = 'sha256')
        new_user = User(username=form.username.data, name=form.name.data, dob=form.dob.data, password_hash=hashed_password, email=form.email.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect("/"+new_user.username+"/home")
    return render_template('register.html',form=form)


class LoginForm(FlaskForm):
    username = StringField('username',validators=[InputRequired(), Length(max=20)])
    password = PasswordField('password',validators=[InputRequired()])
    remember = BooleanField('Remember Me')

@app.route('/user/login', methods = ['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect("/"+current_user.username+"/home")
    form = LoginForm()
    if form.validate_on_submit():
        print('validated')
        user = User.query.filter_by(username = form.username.data).first()
        print(user)
        if user:
            if check_password_hash(user.password_hash,form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect("/"+user.username+"/home")
        flash('Invalid username or password')
        return render_template('login.html',form=form)
    return render_template('login.html',form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return '<h1>you are registered</h1>'

@app.route('/<user_name>/logout')
@login_required
def logout(user_name):
    logout_user()
    return redirect('/user/login')


class DeleteForm(FlaskForm):
    username = StringField('username',validators=[InputRequired(), Length(max=20)])

@app.route('/user/delete',  methods = ['POST', 'GET'])
def delete_user():
    form = DeleteForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        db.session.delete(user)
        db.session.commit()
        return render_template('delete_user.html',users = User.query.all(),form=form)
    return render_template('delete_user.html',users = User.query.all(), form=form)


class UpdateForm(FlaskForm):
    username = StringField('username',validators=[InputRequired(), Length(max=30)])
    dob = DateField('Date Of Birth', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    name = StringField('Name', validators=[InputRequired(), Length(max=64)])

@app.route('/<user_name>/update_information', methods = ['POST', 'GET'])
@login_required
def update_information(user_name):
    print(user_name)
    form = UpdateForm(username=current_user.username, dob=current_user.dob, email=current_user.email, name=current_user.name)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.dob = form.dob.data
        current_user.email = form.email.data
        current_user.name = form.name.data
        db.session.commit()
        return redirect("/"+user_name+"/home")
    return render_template('update_user_information.html',current_user=current_user, form=form, username=user_name)


### ENDS here

if __name__ == '__main__':
    db.init_app(app=app)
    db.create_all(app=app)

    app.run(debug=True)
