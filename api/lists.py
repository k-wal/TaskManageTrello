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

class EditListForm(FlaskForm):
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
        return redirect(url_for('task_blueprint.go_home', user_name=user_name))
    return render_template('add_lists.html',form=form, username=user_name)

@list_blueprint.route('/<user_name>/list/<list_id>',methods=['POST','GET'])
@login_required
def show_list(user_name,list_id):
    userid=User.query.filter(User.username==user_name).first().id
    current_list = List.query.get(list_id)
    tasks=Task.query.filter(Task.list_id==list_id)
    return render_template('show_list.html',user=current_user,list=List.query.get(list_id), list_id=list_id,tasks=tasks)

@list_blueprint.route('/<user_name>/list/<list_id>/list_update', methods=['POST', 'GET'])
@login_required
def update_list(user_name, list_id):
    current_list=List.query.get(list_id)
    form = EditListForm(name = current_list.name, description = current_list.description)
    if form.validate_on_submit():
        current_list.name = form.name.data
        current_list.description = form.description.data
        db.session.commit()
        return redirect(url_for('list_blueprint.show_list', user_name=user_name, list_id=list_id))
    return render_template('update_list.html', username=user_name, list_id=list_id, list=current_list, form=form)



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

class TempAddUserForm(FlaskForm):
    add_user = StringField('Add User :',validators=[InputRequired()])
    
@list_blueprint.route('/<user_name>/list/<list_id>/add_user',methods=['POST','GET'])
@login_required
def add_user(user_name,list_id):
    following = current_user.all_followed()
    user = User.query.filter_by(username = user_name).first()
    current_list = List.query.get(list_id)
    form = TempAddUserForm()
    if form.validate_on_submit():
        current_list.add_user(User.query.filter(User.username == form.add_user.data).first())
        db.session.commit()
        return render_template('add_user_to_list.html',user=user, username=user.username,following=following,form=form,list=current_list,all_users=current_list.return_all_users())
    return render_template('add_user_to_list.html',user=user,username=user.username,following=following,form=form,list=current_list,all_users=current_list.return_all_users())

@list_blueprint.route('/<user_name>/all_lists',methods=['POST','GET'])
@login_required
def show_shared_lists(user_name):
    user = User.query.filter(User.username == user_name).first()
    all_lists = user.return_all_lists()
    return render_template('show_shared_lists.html',user=user,all_lists=all_lists)

