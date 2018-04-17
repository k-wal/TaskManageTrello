from flask import Blueprint, render_template, url_for, request, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import Email, EqualTo, Length, Required, InputRequired
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import db, User, Task, List, Notif

task_blueprint = Blueprint('task_blueprint', __name__)


class TaskForm(FlaskForm):
    deadline = DateField('Deadline', validators=[InputRequired()])
    name = StringField('Task', validators=[InputRequired(), Length(max=100)])
    description = StringField('Description', validators=[Length(max=200)])
    status = SelectField('Status', choices=[('Pending', 'Pending'), ('Ongoing', 'Ongoing'), ('Completed', 'Completed')], default='Pending')
    priority = BooleanField('Priority')
    incentive = StringField('Incentives', validators=[Length(max=200)])
    consequences = StringField('Consequences', validators=[Length(max=200)])

class FilterForm(FlaskForm):
    deadline_start = DateField('Deadline From')
    deadline_end = DateField('Deadline Till')
    completed = BooleanField('Completed',default=True)
    ongoing = BooleanField('Ongoing',default=True)
    pending = BooleanField('Pending',default=True)
    priority_yes = BooleanField('Priority',default=True)
    priority_no = BooleanField('Not Priority',default=True)

class SortForm(FlaskForm):
    criteria = SelectField('Sort by:', choices=[('Deadline(near)','Deadline(near)'),('Deadline(far)','Deadline(far)'),('Name(A-Z)','Name(A-Z)'),('Name(Z-A)','Name(Z-A)')],default='Name(A-Z)')

class EditTaskForm(FlaskForm):
    deadline = DateField('Deadline', validators=[InputRequired()])
    name = StringField('Task', validators=[InputRequired(), Length(max=100)])
    description = StringField('Description', validators=[Length(max=200)])
    status = SelectField('Status', choices=[('Pending', 'Pending'), ('Ongoing', 'Ongoing'), ('Completed', 'Completed')], default='Pending')
    priority = BooleanField('Priority')
    incentive = StringField('Incentives', validators=[Length(max=200)])
    consequences = StringField('Consequences', validators=[Length(max=200)])

class TaskDependencyForm(FlaskForm):
    name = StringField('Task', validators=[InputRequired(), Length(max=100)])



@task_blueprint.route('/<user_name>/list/<list_id>/newtask', methods = ['POST', 'GET'])
@login_required
def add_task(user_name, list_id):
    userid=User.query.filter(User.username==user_name).first().id
    form=TaskForm()
    if form.validate_on_submit():
        new_task = Task(user_id=userid,deadline=form.deadline.data,name=form.name.data,description=form.description.data,status=form.status.data,priority=form.priority.data,incentive=form.incentive.data,consequences=form.consequences.data,list_id=list_id)
        print(new_task)
        db.session.add(new_task)
        db.session.commit()
        new_task.set_relpriority()
        return redirect("/"+user_name+"/list/"+list_id)
    return render_template('newtask.html',form=form, username=user_name, list_id=list_id)

@task_blueprint.route('/<user_name>/home',methods=['POST','GET'])
@login_required
def go_home(user_name):
    userid=User.query.filter(User.username==user_name).first().id
    sort_form=SortForm()
    Tasks=Task.query.filter(Task.user_id==userid)
    print(Tasks)
    notifs=Notif.query.filter(Notif.user_id == userid, Notif.status == 'Unread').order_by(Notif.create_time)
    lists = List.query.filter(List.user_id==userid)
    tasks_of_lists = []
    for list in lists:
        tasks_of_lists.append((list,Task.query.filter(Task.list_id==list.id).order_by(Task.relpriority)))

    print (tasks_of_lists)
    for tasker in tasks_of_lists:
        for task1 in tasker[1]:
            print(tasker[0],task1.name)
        print('\n\n\n\n')
    lists = List.query.filter(List.user_id==userid)

    if sort_form.validate_on_submit():
        if sort_form.criteria.data == 'Deadline(near)':
            tasks=Task.query.filter(Task.user_id==userid).order_by(Task.deadline)

        if sort_form.criteria.data == 'Deadline(far)':
            tasks=Task.query.filter(Task.user_id==userid).order_by(Task.deadline.desc())

        if sort_form.criteria.data == 'Name(A-Z)':
            tasks=Task.query.filter(Task.user_id==userid).order_by(Task.name)
            #print('****************')
            #print(tasks)
            #print('****************')

        if sort_form.criteria.data == 'Name(Z-A)':
            tasks=Task.query.filter(Task.user_id==userid).order_by(Task.name.desc())


        return render_template('home.html',notifs=notifs,sort_form=sort_form,user=User.query.get(userid),tasks=tasks, lists=lists, tasks_of_lists=tasks_of_lists)

    return render_template('home.html',notifs=notifs, sort_form=sort_form,user=User.query.get(userid),tasks=Tasks,lists=lists, tasks_of_lists=tasks_of_lists)

@task_blueprint.route('/<user_name>/list/<list_id>/task/<task_id>',methods=['POST','GET'])
@login_required
def show_task(user_name,task_id,list_id):
    list=List.query.get(list_id)
    userid=User.query.filter(User.username==user_name).first().id
    owner=User.query.get(list.user_id)
    is_owner = False
    if list.user_id == userid:
        is_owner = True
    return render_template('showtask.html',is_owner=is_owner,owner=owner,list=list,list_id=list_id,user=User.query.get(userid),task=Task.query.get(task_id),task_id=task_id)


@task_blueprint.route('/<user_name>/list/<list_id>/task/<task_id>/edit',methods=['POST','GET'])
@login_required
def edit_task(user_name,task_id,list_id):
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
        return redirect("/"+user_name+"/list/"+list_id)
    return render_template('edit_task.html',form=form, username=user_name,task_id=task_id,list_id=list_id)

@task_blueprint.route('/<user_name>/list/<list_id>/task/<task_id>/delete',methods=['POST','GET'])
@login_required
def go_to_delete(user_name,task_id,list_id):
    return render_template('delete_task.html',username=user_name,task=Task.query.get(task_id),task_id=task_id,list_id=list_id)

@task_blueprint.route('/<user_name>/list/<list_id>/task/<task_id>/task_deleted',methods=['POST','GET'])
@login_required
def delete_task(user_name,task_id,list_id):
    db.session.delete(Task.query.get(task_id))
    db.session.commit()
    return render_template('task_deleted.html',username=user_name,list_id=list_id)

@task_blueprint.route('/<user_name>/list/<list_id>/task/<task_id>/dependency',methods=['POST','GET'])
@login_required
def dependent(user_name,task_id,list_id):
    tasks = Task.query.filter(Task.user_id==current_user.id)
    current_task = Task.query.get(task_id)
    alltasks=[]
    for task in tasks:
        if not current_task.is_dependent(task) and task.list_id == current_task.list_id:
            alltasks.append(task)
    deptask = current_task.all_dependent()
    return render_template('task_dependency.html', list_id=list_id,username=user_name, deptask=deptask, alltasks=alltasks, current_task=current_task, task_id=task_id)

@task_blueprint.route('/<user_name>/list/<list_id>/task/<task_id>/add_dep=<dep_id>',methods=['POST','GET'])
@login_required
def add_dependency(user_name,task_id,list_id,dep_id):
    current_task = Task.query.get(task_id)
    deptask = Task.query.get(dep_id)
    if deptask:
        current_task.dependent_on(deptask)
    db.session.commit()
    return redirect('/'+user_name+'/list/'+list_id+'/task/'+task_id+'/dependency')


@task_blueprint.route('/<user_name>/list/<list_id>/task/<task_id>/remove_dep=<dep_id>',methods=['POST','GET'])
@login_required
def remove_dependency(user_name,task_id,list_id,dep_id):
    current_task = Task.query.get(task_id)
    deptask = Task.query.get(dep_id)
    current_task.remove_dependency(deptask)
    db.session.commit()
    return redirect('/'+user_name+'/list/'+list_id+'/task/'+task_id+'/dependency')

@task_blueprint.route('/<user_name>/search_tasks')
@login_required
def search_tasks(user_name):
    to_search=request.args.get('query')
    user=User.query.filter(User.username==user_name).first()
    Tasks = Task.query.filter(Task.user_id==user.id)
    tasks=[]
    for task in Tasks:
        if to_search in task.name or to_search in task.description:
            tasks.append(task)

    sort_form=SortForm()
    filter_form=FilterForm()
    Tasks=tasks
    return render_template('home.html', sort_form=sort_form,user=user,tasks=Tasks,filter_form=filter_form)

@task_blueprint.route('/<user_name>/list/<list_id>/reorder=<task1_id>-<task2_id>')
@login_required
def reorder_tasks(user_name, task1_id, task2_id, list_id):
    task1 = Task.query.get(task1_id)
    task2 = Task.query.get(task2_id)
    if task1.list_id != task2.list_id:
        return '<h1>Tasks do not belong to same list</h1>'
    else:
        temp = task1.relpriority
        task1.relpriority = task2.relpriority
        task2.relpriority = temp
        db.session.commit()
    return redirect(url_for('list_blueprint.show_list',user_name=user_name, list_id=list_id))

@task_blueprint.route('/<user_name>/list/<list_id>/task/mark_complete=<task_id>')
@login_required
def mark_complete(user_name, task_id, list_id):
    current_task = Task.query.get(task_id)
    list = List.query.get(list_id)
    user=User.query.filter(User.username==user_name).first()
    deptask=[]
    flag=0
    for task in current_task.all_dependent():
        if task.status != 'Completed' and task.id != current_task.id:
            deptask.append(task)
            flag = 1

    if(flag == 0):
        current_task.status = 'Completed'
        db.session.commit()
        return redirect(url_for('list_blueprint.show_list',user_name=user_name, list_id=list_id))
    return render_template('dependent_tasks_left.html',user=user,list=list,tasks=deptask,current_task = current_task)
