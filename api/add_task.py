from flask import Blueprint, render_template, url_for, request, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import Email, EqualTo, Length, Required, InputRequired
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

@task_blueprint.route('/<use_id>/newtask', methods = ['POST', 'GET'])
def add_task(use_id):
    form=TaskForm()
    if form.validate_on_submit():
        new_task = Task(user_id=use_id,deadline=form.deadline.data,name=form.name.data,description=form.description.data,status=form.status.data,priority=form.priority.data,incentive=form.incentive.data,consequences=form.consequences.data)
        db.session.add(new_task)
        db.session.commit()
        print("**************")
        print(use_id)
        return redirect("/"+str(use_id)+"/home")
    return render_template('newtask.html',form=form, user_id=use_id)

@task_blueprint.route('/<use_id>/home',methods=['POST','GET'])
def go_home(use_id):
    print(use_id)
    return render_template('home.html',user=User.query.get(use_id),tasks=Task.query.filter(Task.user_id==use_id))


