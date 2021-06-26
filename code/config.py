import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY=os.urandom(24)
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:12345678@msds603.c08ct9wmukfr.us-west-2.rds.amazonaws.com:5432/postgres'
    SQLALCHEMY_TRACK_MODIFICATIONS = True # flask-login uses sessions which require a secret Key
