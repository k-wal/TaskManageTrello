from flask import Blueprint, render_template, url_for, request, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import Email, EqualTo, Length, Required, InputRequired
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import db, User, Task, List, Notif, Message
from sqlalchemy import or_

message_blueprint = Blueprint('message_blueprint', __name__)

class NewMessageForm(FlaskForm):
    content = StringField('Write message', validators=[InputRequired(), Length(max=200)])

@login_required
@message_blueprint.route('/<user_name>/show_friends_to_message', methods = ['POST', 'GET'])
def show_friends_to_message(user_name):
	user = User.query.filter(User.username==user_name).first()
	friends = user.all_followed()
	return render_template('show_friends_to_message.html',user=user,friends=friends)

@login_required
@message_blueprint.route('/<user_name>/messages', methods = ['POST', 'GET'])
def messages_home(user_name):
	return redirect(url_for('message_blueprint.show_friends_to_message',user_name=user_name))

@login_required
@message_blueprint.route('/<user_name>/messages/<friend_username>', methods = ['POST', 'GET'])
def show_friend_messages(user_name,friend_username):
	user = User.query.filter(User.username==user_name).first()
	friend = User.query.filter(User.username==friend_username).first()
	form=NewMessageForm(content='')
	messages1 = Message.query.filter(Message.to_username==friend_username,Message.from_username==user_name).order_by(Message.create_time) 
	messages2 = Message.query.filter(Message.from_username==friend_username,Message.to_username==user_name).order_by(Message.create_time)
	m1=[]
	m2=[]
	for message in messages1:
		m1.append(message)
	for message in messages2:
		m2.append(message)
	messages = m1
	messages.extend(m2)
	newlist = sorted(messages, key=lambda k: k.create_time)
	messages=newlist 
	if form.validate_on_submit():
		new_message = Message(from_username=user.username,content=form.content.data,to_username=friend.username)
		db.session.add(new_message)
		db.session.commit()
		messages1 = Message.query.filter(Message.to_username==friend_username,Message.from_username==user_name).order_by(Message.create_time) 
		messages2 = Message.query.filter(Message.from_username==friend_username,Message.to_username==user_name).order_by(Message.create_time)
		m1=[]
		m2=[]
		for message in messages1:
			m1.append(message)
		for message in messages2:
			m2.append(message)
		messages = m1
		messages.extend(m2)
		newlist = sorted(messages, key=lambda k: k.create_time)
		messages=newlist 
		return render_template('show_friend_messages.html',form=form,friend=friend,user=user,messages=messages)
	return render_template('show_friend_messages.html',form=form,friend=friend,user=user,messages=messages)        