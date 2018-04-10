import os
from flask import request
from flask import current_app as app
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, url_for, request, redirect, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import Email, EqualTo, Length, Required, InputRequired
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import db, User, Task


image_blueprint = Blueprint('image_blueprint', __name__)
# basedir = os.path.abspath(os.path.dirname(__file__))
# UPLOAD_FOLDER = basedir+'/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@image_blueprint.route('/<user_name>/uploads', methods=['GET', 'POST'])
@login_required
def upload_file(user_name):
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = current_user.username + '.' + filename.rsplit('.', 1)[1].lower()
            print('before')
            print(os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], filename)))
            if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print('after')
            print(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)))
            print(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            current_user.profile_picture = 'static/'+filename
            file.save(current_user.profile_picture)
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            db.session.commit()
            return redirect(url_for('task_blueprint.go_home', user_name=current_user.username))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

from flask import send_from_directory

@image_blueprint.route('/<user_name>/uploads/<filename>')
@login_required
def uploaded_file(user_name,filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)
