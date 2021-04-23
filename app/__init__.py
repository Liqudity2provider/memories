from datetime import datetime
from flask import Flask
from sqlalchemy.orm import sessionmaker
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from flask_login import LoginManager
from flask_mail import Mail
from flask_marshmallow import Marshmallow
from app.config import Config


db = SQLAlchemy()
engine = create_engine('sqlite:///login.db', echo=False)
Base = declarative_base()

Base.metadata.create_all(engine)


bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    from app.users.routes import users
    from app.post.routes import posts
    from app.main.routes import main
    from app.errors.handlers import errors
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app
