import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = """postgresql://v2_db:swolemate@msds603v2.c08ct9wmukfr.us-west-2.rds.amazonaws.com/postgres"""
    # flask-login uses sessions which require a secret Key
    SQLALCHEMY_TRACK_MODIFICATIONS = True
