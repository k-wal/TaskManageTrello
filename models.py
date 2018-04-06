from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy, event
from sqlalchemy import engine

db = SQLAlchemy()

# noinspection PyUnusedLocal
@event.listens_for(engine.Engine, 'connect')
def __set_sqlite_pragma(db_conn, conn_record):
    cursor = db_conn.cursor()
    cursor.execute('PRAGMA foreign_keys=ON;')
    cursor.close()

class User(UserMixin, db.Model):
    id = db.Column('user_id', db.Integer, primary_key=True, autoincrement=True)
    username = db.Column('username', db.String(64), unique=True, nullable=False)
    name = db.Column('name', db.String(120), unique=False, nullable=False)
    dob = db.Column('date_of_birth', db.DateTime, nullable=False)
    registration_time = db.Column('registration_time',db.DateTime, default=datetime.utcnow)
    password_hash = db.Column('password_hash',db.String(80), nullable=False)
    remember_me = db.Column('remember_me', db.Boolean, unique=False, default=False)

    tasks = db.relationship(
        'Task',
        backref=db.backref('user-table', lazy='joined'),
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    @classmethod
    def hash_password(cls, password):
        return generate_password_hash(password, method='sha256')

    def check_password(self,password):
        return check_password_hash(self.password_hash, password)

    def serialize(self):
        return {
            'user_id' : self.user_id,
            'username' : self.username,
            'name' : self.name,
            'dob' : self.dob,
            'registration_time' : self.registration_time,
            'password_hash' : self.password_hash,
            'remember_me' : self.remember_me
        }

    def __repr__(self):
        return self.serialize().__repr__()

class Task(db.Model):

    __tablename__ = 'task-table'

    id = db.Column('task_id', db.Integer, primary_key=True, autoincrement=True)
    start_time = db.Column('start_time', db.DateTime)
    end_time = db.Column('end_time', db.DateTime)
    deadline = db.Column('deadline', db.DateTime, nullable=False)
    user_id = db.Column('user_id', db.Integer, db.ForeignKey(
        'user-table', ondelete='CASCADE'), nullable=False)
    name = db.Column('name', db.String(100), nullable=False)
    description = db.Column('description', db.String(200))
    status = db.Column('status', db.Enum(
        *['Pending', 'Ongoing', 'Completed']), nullable=False, default='Pending')
    priority = db.Column('priority', db.Boolean, nullable=False, default=False)
    incentive = db.Column('incentive', db.String(200))
    consequences = db.Column('consequences', db.String(200))

    def serialize(self):
        return {
            'task_id': self.task_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'deadline': self.deadline,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'incentive': self.incentive,
            'consequences': self.consequences
        }

    def __repr__(self):
        return self.serialize().__repr__()
