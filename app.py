from flask import Flask, Blueprint, render_template, url_for, request, redirect, flash
from config.config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from api.user_registration import user_blueprint
from api.upload_profile_images import image_blueprint
from api.add_task import task_blueprint
from api.lists import list_blueprint
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.fields.html5 import DateField
from wtforms.validators import Email, EqualTo, Length, Required, InputRequired
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import db, User, Task, List
import os
from flask import request
from werkzeug.utils import secure_filename
from flask_uploads import UploadSet, IMAGES, configure_uploads

UPLOAD_FOLDER ='static/images'
# basedir = os.path.abspath(os.path.dirname(__file__))
# UPLOAD_FOLDER = 'static/'

app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#

# db = SQLAlchemy(app)
# migrate = Migrate(app, db)

#NEED TO FIND OUT HOW @login_required for blueprints
# app.register_blueprint(user_blueprint)
app.register_blueprint(task_blueprint)
app.register_blueprint(image_blueprint)
app.register_blueprint(list_blueprint)

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
    return redirect('/index')


class DeleteForm(FlaskForm):
    username = StringField('username',validators=[InputRequired(), Length(max=20)])

@app.route('/user/delete',  methods = ['POST', 'GET'])
def delete_user():
    form = DeleteForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user:
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
        return redirect("/"+form.username.data+"/home")
    return render_template('update_user_information.html',current_user=current_user, form=form, username=user_name)

class FollowForm(FlaskForm):
    username = StringField('username',validators=[InputRequired(), Length(max=30)])

@app.route('/<user_name>/follow', methods = ['POST', 'GET'])
@login_required
def go_to_follow(user_name):
    following = current_user.all_followed()
    return render_template('follow.html',users=[],username=user_name,following=following)

@app.route('/<user_name>/follow/search_users')
@login_required
def search_tasks(user_name):
    to_search=request.args.get('query')
    following = current_user.all_followed()
    print(to_search)
    users=[]
    Users=User.query.all()
    for user in Users:
        print(user.name)
        if user.username is not user_name:
            if to_search in user.name or to_search in user.username:
                users.append(user)
    return render_template('follow.html',users=users,username=user_name,following=following)


@app.route('/<user_name>/follow=<to_follow>', methods = ['POST', 'GET'])
@login_required
def follow_user(user_name,to_follow):
    following = current_user.all_followed()
    user = User.query.filter_by(username = to_follow).first()
    print(user)
    current_user.follow(user)
    db.session.commit()
    return render_template('now_following_message.html',username=user_name,user=user)

@app.route('/<user_name>/following', methods = ['POST', 'GET'])
@login_required
def following(user_name):
    following = current_user.all_followed()
    return render_template('following.html',following=following,username=user_name)

class TempListChangeForm(FlaskForm):
    new_list = StringField('New List',validators=[InputRequired()])

@app.route('/<user_name>/list/<list_id>/task/<task_id>/shift_lists',methods=['POST','GET'])
@login_required
def shift_lists(user_name,task_id,list_id):
    userid=User.query.filter(User.username==user_name).first().id
    current_task=Task.query.get(task_id)
    current_list=List.query.get(list_id)
    all_lists=List.query.filter(List.user_id == userid)
    form=TempListChangeForm(new_list=current_list.name)
    if form.validate_on_submit():
        current_task.list_id = List.query.filter(List.name == form.new_list.data).first().id
        db.session.commit() 
        return redirect("/"+user_name+"/list/"+str(current_task.list_id)+"/task/"+task_id)
    return render_template('shift_task_to_list.html',form=form, username=user_name,task_id=task_id,list_id=list_id,task=current_task,list=current_list,all_lists=all_lists)

@app.route('/<user_name>/try_search_jquery',methods=['POST','GET'])
@login_required
def jquery_search(user_name):   
    user_id = current_user.id
    availableTags=[]
    for task in Task.query.filter(Task.user_id == user_id):
        availableTags.append(task.name)
    print(availableTags)
    return render_template('auto.html',availableTags=availableTags)


### ENDS here

if __name__ == '__main__':
    db.init_app(app=app)
    db.create_all(app=app)

    app.run(debug=True)
