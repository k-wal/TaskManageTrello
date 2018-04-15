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
        new_list.add_user(User.query.get(userid))
        db.session.commit()
        print('list added')
        return redirect(url_for('task_blueprint.go_home', user_name=user_name))
    return render_template('add_lists.html',form=form, username=user_name)

@list_blueprint.route('/<user_name>/list/<list_id>',methods=['POST','GET'])
@login_required
def show_list(user_name,list_id):
    userid=User.query.filter(User.username==user_name).first().id
    current_list = List.query.get(list_id)
    is_owner = False
    creater = User.query.get(current_list.user_id)
    if current_list.user_id == userid:
        is_owner = True
    tasks=Task.query.filter(Task.list_id==list_id).order_by(Task.relpriority)
    return render_template('show_list.html',creater=creater,is_owner = is_owner,user=current_user,list=List.query.get(list_id), list_id=list_id,tasks=tasks)

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
    
@list_blueprint.route('/<user_name>/list/<list_id>/see_shared',methods=['POST','GET'])
@login_required
def see_users(user_name,list_id):
    user = User.query.filter_by(username = user_name).first()
    current_list = List.query.get(list_id)
    following = current_user.all_followed()
    #print(following)
    following_not_list = []
    is_owner = False
    if current_list.user_id == user.id:
        is_owner = True
    for cur_user in following:
        #print(cur_user)
        if not current_list.is_user(cur_user):
            following_not_list.append(cur_user)
    return render_template('add_user_to_list.html',is_owner=is_owner,user=user,username=user.username,following=following_not_list,list=current_list,all_users=current_list.return_all_users())

@list_blueprint.route('/<user_name>/list/<list_id>/add=<to_add>',methods=['GET','POST'])
@login_required
def add_user(user_name,list_id,to_add):
    current_list = List.query.get(list_id)
    user = User.query.filter(User.username == to_add).first()
    current_list.add_user(user)
    db.session.commit()
    return redirect('/'+user_name+'/list/'+list_id+'/see_shared')



@list_blueprint.route('/<user_name>/all_lists',methods=['POST','GET'])
@login_required
def show_shared_lists(user_name):
    user = User.query.filter(User.username == user_name).first()
    all_lists = user.return_all_lists()
    return render_template('show_shared_lists.html',user=user,all_lists=all_lists)

@list_blueprint.route('/<user_name>/list/<list_id>/remove=<to_remove>',methods=['POST','GET'])
@login_required
def remove_user_from_list(user_name,list_id,to_remove):
    current_list = List.query.get(list_id)
    cur_user = User.query.filter(User.username == to_remove).first()
    current_list.remove_user(cur_user)
    db.session.commit()
    #return 'removed'
    return redirect('/'+user_name+'/list/'+list_id+'/see_shared')
@list_blueprint.route('/<user_name>/exit=<list_id>',methods=['POST','GET'])
@login_required
def exit_list(user_name,list_id):
    current_list = List.query.get(list_id)
    cur_user = User.query.filter(User.username == user_name).first()
    current_list.remove_user(cur_user)
    db.session.commit()
    return redirect('/'+user_name+'/all_lists')

class SortForm(FlaskForm):
    criteria = SelectField('Sort by:', choices=[('Deadline(near)','Deadline(near)'),('Deadline(far)','Deadline(far)'),('Name(A-Z)','Name(A-Z)'),('Name(Z-A)','Name(Z-A)')],default='Name(A-Z)')

@list_blueprint.route('/<user_name>/search_lists')
@login_required
def search_lists(user_name):
    to_search=request.args.get('query')
    user=User.query.filter(User.username==user_name).first()
    Lists = List.query.filter(List.user_id==user.id)
    lists=[]
    for list in Lists:
        if to_search in list.name or to_search in list.description:
            lists.append(list)

    sort_form=SortForm()
    Lists=lists
    return render_template('home.html', sort_form=sort_form,user=user,lists=Lists)
