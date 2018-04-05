from flask import Flask
from config.config import Config
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from api.user_registration import user_blueprint
from models import db

app = Flask(__name__)
app.config.from_object(Config)
# db = SQLAlchemy(app)
# migrate = Migrate(app, db)
app.register_blueprint(user_blueprint)

if __name__ == '__main__':
    db.init_app(app=app)
    db.create_all(app=app)

    app.run(debug=True)
