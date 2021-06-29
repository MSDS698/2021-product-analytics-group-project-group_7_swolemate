from flask import Flask
import os
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

# Initialization
# Create an application instance, handles all requests.
application = Flask(__name__)
application._static_folder = 'static'
#application.secret_key = os.urandom(24)
application.config.from_object(Config)
db = SQLAlchemy(application)
db.create_all()
db.session.commit()


# login_manager needs to be initiated before running the app
login_manager = LoginManager()
login_manager.init_app(application)

bootstrap = Bootstrap(application)

# routes.py needs to import "application" variable in __init__.py - breaks PEP8
from app import classes
from app import routes
