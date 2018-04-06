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

    @classmethod
    def hash_password(cls, password):
        print("***")
        print("***")
        print("***")
        print("***")
        print("PASSWORD: %s" % password)
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
