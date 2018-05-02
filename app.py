from flask import Flask, Blueprint, render_template, url_for, request, redirect, flash
from config.config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
import json
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from api.user_registration import user_blueprint
from api.upload_profile_images import image_blueprint
from api.add_task import task_blueprint
from api.comments import comment_blueprint
from api.lists import list_blueprint
from api.notifications import notif_blueprint
from api.messages import message_blueprint
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.fields.html5 import DateField
from wtforms.validators import Email, EqualTo, Length, Required, InputRequired
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import db, User, Task, List, Connection, Notif
import os
from flask import request
from werkzeug.utils import secure_filename
from flask_uploads import UploadSet, IMAGES, configure_uploads
from api.friends import is_friends_or_pending, get_friend_requests,get_friends, get_recieved_requests
from datetime import datetime, timedelta
from flask_mail import Mail, Message

UPLOAD_FOLDER ='static/images'
# basedir = os.path.abspath(os.path.dirname(__file__))
# UPLOAD_FOLDER = 'static/'

app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'ergocompito@gmail.com'
app.config['MAIL_PASSWORD'] = 'aadilanshita'

mail = Mail(app)


#

# db = SQLAlchemy(app)
# migrate = Migrate(app, db)

#NEED TO FIND OUT HOW @login_required for blueprints
# app.register_blueprint(user_blueprint)
app.register_blueprint(task_blueprint)
app.register_blueprint(image_blueprint)
app.register_blueprint(list_blueprint)
app.register_blueprint(comment_blueprint)
app.register_blueprint(notif_blueprint)
app.register_blueprint(message_blueprint)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)

### FROM api.user_registration
@app.route('/')
@app.route('/index')
def index():
    ###performing a check for all the users that have deadlines coming up and sending them mails.
    current_date = datetime.utcnow()
    date_2_days = datetime.now() + timedelta(days=2)
    dates = Task.query.filter(Task.deadline.between(current_date,date_2_days))
    emails = []
    for date in dates:
        uid = date.user_id
        u = User.query.filter(User.id == uid).first()
        if u.email not in emails:
            emails.append(u.email)
        if emails:
            msg = Message('test subject', sender='aadilmehdis@gmail.com', recipients=emails)
            msg.body = 'text body'
            msg.html = '''
                <h1>This is an email from Ergo/Compito App.</h1>
                <p style='color:'red'>You have pending work and fast approaching deadlines.</p>
                <p style='color:'purple'>Get your ass up your chair and work. Login now </p>
            '''
            mail.send(msg)
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
def search_users(user_name):
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

############# adding friends

class FriendForm(FlaskForm):
    username = StringField('username',validators=[InputRequired(), Length(max=20)])

@app.route("/<user_name>/add_friend=<to_friend>", methods=['GET','POST'])
@login_required
def add_friend(user_name,to_friend):

    user_a_id = current_user.id
    user_b = User.query.filter_by(username = to_friend).first()
    user_b_id = user_b.id
       # Check connection status between user_a and user_b
    is_friends, is_pending, is_friends_reverse = is_friends_or_pending(user_a_id, user_b_id)
    msg=current_user.name + " sent you a friend request."
    new_notif = Notif(user_id=user_b.id, content=msg, typ='Request', second_username=current_user.username)
    db.session.add(new_notif)
    db.session.commit()

    if user_a_id == user_b_id:
        return render_template('now_following_message.html',message='You cannot add yourself as a friend.',user_name=user_name,user=user_b)
    elif is_friends or is_friends_reverse:
        return render_template('now_following_message.html',message='You are already friends.',user_name=user_name,user=user_b)
    elif is_pending:
        return render_template('now_following_message.html',message='Your friend request is pending.',user_name=user_name,user=user_b)

    else:
        requested_connection = Connection(user_a_id=user_a_id,
                                          user_b_id=user_b_id,
                                          status="Requested")
        db.session.add(requested_connection)
        db.session.commit()
        print ("User ID %s has sent a friend request to User ID %s" % (user_a_id, user_b_id))
        return render_template('now_following_message.html',message='Request sent.',user_name=user_name,user=user_b)


@app.route("/<user_name>/friend_requests", methods=['GET','POST'])
@login_required
def show_friend_requests(user_name):
    received_friend_requests = get_recieved_requests(current_user.id)
    return render_template('friend_requests.html', friendrequests=received_friend_requests, user_name=user_name)

@app.route("/<user_name>/accept=<friend_id>", methods=['GET','POST'])
@login_required
def accept_friend_request(user_name, friend_id):
    user_a_id = friend_id
    user_b_id = current_user.id;
    relation = db.session.query(Connection).filter(Connection.user_a_id == user_a_id, Connection.user_b_id == user_b_id).first()
    relation.status = 'Accepted'
    user = User.query.get(user_a_id)
    current_user.follow(user)
    user.follow(current_user)
    db.session.commit()
    msg=current_user.name + " has accepted your friend request"
    new_notif = Notif(user_id=friend_id, content=msg, typ='Accepted',second_username=current_user.username)
    db.session.add(new_notif)
    db.session.commit()
    return redirect(url_for('show_friend_requests', user_name=user_name))

@app.route("/<user_name>/decline=<friend_id>", methods=['GET','POST'])
@login_required
def decline_friend_request(user_name, friend_id):
    user_a_id = friend_id
    user_b_id = current_user.id;
    db.session.query(Connection).filter(Connection.user_a_id == user_a_id, Connection.user_b_id == user_b_id).delete()
    db.session.commit()
    return redirect(url_for('show_friend_requests', user_name=user_name))

@app.route("/<user_name>/friends")
@login_required
def show_friends(user_name):
    following = current_user.all_followed()
    return render_template('following.html',following=following,username=user_name)

@app.route("/<user_name>/unfriend=<friend_id>", methods=['GET','POST'])
@login_required
def unfriend(user_name,friend_id):
    user = User.query.get(friend_id)
    current_user.unfollow(user)
    user.unfollow(current_user)
    relationleft = db.session.query(Connection).filter(Connection.user_a_id == current_user.id, Connection.user_b_id == friend_id).first()
    relationright = db.session.query(Connection).filter(Connection.user_a_id == friend_id, Connection.user_b_id == current_user.id).first()
    if relationleft:
        relationleft.status = 'Unfriended'
    if relationright:
        relationright.status = 'Unfriended'
    db.session.commit()
    return redirect(url_for('show_friends', user_name=user_name))

@app.route("/<user_name>/friend_profile/<friend_username>",methods=['GET','POST'])
@login_required
def friend_profile(user_name,friend_username):
    friend = User.query.filter(User.username == friend_username).first()
    user = User.query.filter(User.username == user_name).first()
    all_lists = user.return_all_lists()
    shared_number = 0
    for list in all_lists:
        if list.is_user(friend):
            shared_number = shared_number + 1

    return render_template('friend_profile.html',shared_number=shared_number,friend=friend,user=user)

def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

@app.route("/show_calander")
def calendar():
    notifs=Notif.query.filter(Notif.user_id == current_user.id, Notif.status == 'Unread').order_by(Notif.create_time)
    countnotifs = 0
    for notif in notifs:
        countnotifs += 1
    return render_template('json.html', user=current_user, notifs=notifs, countnotifs=countnotifs)


@app.route("/data")
@login_required
def getevents():
    start_date = request.args.get('start', '')
    end_date = request.args.get('end', '')
    try:
        os.remove('calanderevents.json')
    except OSError:
        pass
    file =  open('calanderevents.json','w+')
    tasks = Task.query.filter(Task.user_id==current_user.id).order_by(Task.relpriority)
    jsonlist = []
    for task in tasks:
        s = "{}-{}-{}".format(task.create_time.year,task.create_time.month,task.create_time.day)
        d = "{}-{}-{}".format(task.deadline.year,task.deadline.month,task.deadline.day)
        print(s,d)
        current_date = datetime.utcnow()
        date_2_days = datetime.now() + timedelta(days=2)
        color = '#007FFF';
        if current_date <= task.deadline <= date_2_days:
            print("kjadfh")
            color = '#DC143C';
        taskobj = {
                    'title':task.name,
                    'start':d,
                    # 'end':d,
                    'id':task.id,
                    'color':color
                  }
    jsonlist.append(taskobj)
    file.write(json.dumps(jsonlist, default = myconverter))
    file.close()
    with open("calanderevents.json", "r") as input_data:
        # you should use something else here than just plaintext
        # check out jsonfiy method or the built in json module
        # http://flask.pocoo.org/docs/0.10/api/#module-flask.json
        return input_data.read()


############################

if __name__ == '__main__':
    db.init_app(app=app)
    db.create_all(app=app)

    app.run(debug=True)
