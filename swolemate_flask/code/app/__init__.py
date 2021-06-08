from flask import Flask
import os

# Initialization
# Create an application instance, handles all requests.
application = Flask(__name__)
application.secret_key = os.urandom(24)

# routes.py needs to import "application" variable in __init__.py - breaks PEP8
from app import routes_2
