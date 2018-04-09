from flask import Blueprint, render_template, url_for, request, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import Email, EqualTo, Length, Required, InputRequired
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import db, User, Task

task_blueprint = Blueprint('task_blueprint', __name__)


class TaskForm(FlaskForm):
    deadline = DateField('Deadline', validators=[InputRequired()])
    name = StringField('Task', validators=[InputRequired(), Length(max=100)])
    description = StringField('Description', validators=[Length(max=200)])
    status = SelectField('Status', choices=[('Pending', 'Pending'), ('Ongoing', 'Ongoing'), ('Completed', 'Completed')], default='Pending')
    priority = BooleanField('Priority')
    incentive = StringField('Incentives', validators=[Length(max=200)])
    consequences = StringField('Consequences', validators=[Length(max=200)])

@task_blueprint.route('/<user_name>/newtask', methods = ['POST', 'GET'])
@login_required
def add_task(user_name):
    userid=User.query.filter(User.username==user_name).first().id
    form=TaskForm()
    if form.validate_on_submit():
        new_task = Task(user_id=userid,deadline=form.deadline.data,name=form.name.data,description=form.description.data,status=form.status.data,priority=form.priority.data,incentive=form.incentive.data,consequences=form.consequences.data)
        db.session.add(new_task)
        db.session.commit()
        return redirect("/"+user_name+"/home")
    return render_template('newtask.html',form=form, username=user_name)

@task_blueprint.route('/<user_name>/home',methods=['POST','GET'])
@login_required
def go_home(user_name):
    userid=User.query.filter(User.username==user_name).first().id
    return render_template('home.html',user=User.query.get(userid),tasks=Task.query.filter(Task.user_id==userid))

@task_blueprint.route('/<user_name>/<task_id>',methods=['POST','GET'])
@login_required
def show_task(user_name,task_id):
    userid=User.query.filter(User.username==user_name).first().id
    return render_template('showtask.html',user=User.query.get(userid),task=Task.query.get(task_id),task_id=task_id)

class EditTaskForm(FlaskForm):
    deadline = DateField('Deadline', validators=[InputRequired()])
    name = StringField('Task', validators=[InputRequired(), Length(max=100)])
    description = StringField('Description', validators=[Length(max=200)])
    status = SelectField('Status', choices=[('Pending', 'Pending'), ('Ongoing', 'Ongoing'), ('Completed', 'Completed')], default='Pending')
    priority = BooleanField('Priority')
    incentive = StringField('Incentives', validators=[Length(max=200)])
    consequences = StringField('Consequences', validators=[Length(max=200)])


@task_blueprint.route('/<user_name>/<task_id>/edit',methods=['POST','GET'])
@login_required
def edit_task(user_name,task_id):
    userid=User.query.filter(User.username==user_name).first().id
    current_task=Task.query.get(task_id)
    form=EditTaskForm(deadline=current_task.deadline,name=current_task.name,description=current_task.description,status=current_task.status,priority=current_task.priority,incentive=current_task.incentive,consequences=current_task.consequences)
    if form.validate_on_submit():
        current_task.name=form.name.data
        current_task.deadline=form.deadline.data
        current_task.description=form.description.data
        current_task.status=form.status.data
        current_task.priority=form.priority.data
        current_task.incentive=form.incentive.data
        current_task.consequences=form.consequences.data
        db.session.commit()
        return redirect("/"+user_name+"/home")
    return render_template('edit_task.html',form=form, username=user_name,task_id=task_id)

@task_blueprint.route('/<user_name>/<task_id>/delete',methods=['POST','GET'])
@login_required
def go_to_delete(user_name,task_id):
    return render_template('delete_task.html',username=user_name,task=Task.query.get(task_id),task_id=task_id)

@task_blueprint.route('/<user_name>/<task_id>/task_deleted',methods=['POST','GET'])
@login_required
def delete_task(user_name,task_id):
    db.session.delete(Task.query.get(task_id))
    db.session.commit()
    return render_template('task_deleted.html',username=user_name)

class TaskDependencyForm(FlaskForm):
    name = StringField('Task', validators=[InputRequired(), Length(max=100)])

@task_blueprint.route('/<user_name>/<task_id>/dependency',methods=['POST','GET'])
@login_required
def dependent(user_name,task_id):
    alltasks = Task.query.filter(Task.user_id==current_user.id)
    form = TaskDependencyForm()
    current_task = Task.query.get(task_id)
    deptask = current_task.all_dependent()
    if form.validate_on_submit():
        task = Task.query.filter(Task.user_id==current_user.id, Task.name==form.name.data).first()
        if task:
            current_task.dependent_on(task)
        db.session.commit()
        return redirect("/"+user_name+'/'+task_id+"/dependency")
    return render_template('task_dependency.html', username=user_name, form=form, deptask=deptask, alltasks=alltasks, current_task=current_task, task_id=task_id)
