from flask import Blueprint, render_template, url_for, request, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import Email, EqualTo, Length, Required, InputRequired
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import db, User, Task, List, Notif

notif_blueprint = Blueprint('notif_blueprint', __name__)

@login_required
@notif_blueprint.route('/<user_name>/notif/mark_read=<notif_id>', methods = ['POST', 'GET'])
def mark_read(user_name,notif_id):
    notif = Notif.query.get(notif_id)
    notif.status = 'Read'
    db.session.commit()
    return redirect(url_for('task_blueprint.go_home',user_name = user_name))

@login_required
@notif_blueprint.route('/<user_name>/see_read_notifs', methods = ['POST', 'GET'])
def see_read_notifs(user_name):
    user = User.query.filter(User.username == user_name).first()
    notifs = Notif.query.filter(Notif.user_id == user.id, Notif.status == 'Read')
    return render_template('read_notifs.html',user=user,notifs=notifs)

@login_required
@notif_blueprint.route('/<user_name>/see_message/<notif_id>', methods = ['POST', 'GET'])
def see_message_notif(user_name,notif_id):
	notif = Notif.query.get(notif_id)
	notif.status='Read'
	db.session.commit()
	return redirect(url_for('message_blueprint.show_friend_messages',user_name=user_name,friend_username=notif.second_username))

@login_required
@notif_blueprint.route('/<user_name>/see_requests/<notif_id>', methods = ['POST', 'GET'])
def see_requests_notif(user_name,notif_id):
	notif = Notif.query.get(notif_id)
	notif.status='Read'
	db.session.commit()
	return redirect('/'+user_name+'/friend_requests')
