from flask import Blueprint, render_template, url_for, request, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import Email, EqualTo, Length, Required, InputRequired
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import db, User, Task, List

list_blueprint = Blueprint('list_blueprint', __name__)

class NewListForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(max=100)])
    description = StringField('Description', validators=[InputRequired(), Length(max=200)])

@login_required
@list_blueprint.route('/<user_name>/addlist', methods = ['POST', 'GET'])
def make_new_list(user_name):
    print('here')
    print(current_user)
    userid=User.query.filter(User.username==user_name).first().id
    form=NewListForm()
    print(form.validate_on_submit())
    if form.validate_on_submit():
        new_list = List(user_id=userid,name=form.name.data,description=form.description.data)
        db.session.add(new_list)
        db.session.commit()
        print('list added')
        return redirect(url_for('task_blueprint.go_home'))
    return render_template('add_lists.html',form=form, username=user_name)

@list_blueprint.route('/<user_name>/list/<list_id>',methods=['POST','GET'])
@login_required
def show_list(user_name,list_id):
    userid=User.query.filter(User.username==user_name).first().id
    current_list = List.query.get(list_id)
    tasks=Task.query.filter(Task.list_id==list_id)
    return render_template('show_list.html',user=current_user,list=List.query.get(list_id), list_id=list_id,tasks=tasks)

@list_blueprint.route('/<user_name>/list/<list_id>/delete',methods=['POST','GET'])
@login_required
def confirm_deletion_list(user_name,list_id):
    return render_template('delete_list.html',user=current_user, name=user_name,list=List.query.get(list_id),list_id=list_id)

@list_blueprint.route('/<user_name>/list/<list_id>/list_deleted',methods=['POST','GET'])
@login_required
def delete_list(user_name,list_id):
    db.session.delete(List.query.get(list_id))
    db.session.commit()
    return render_template('list_deleted.html',user=current_user,username=user_name, list=List.query.get(list_id))
