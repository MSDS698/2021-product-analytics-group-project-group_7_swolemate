#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 14 19:12:57 2021

@author: danielcarrera
"""
  
from app import classes
from app import db
from config import Config
from flask_sqlalchemy import SQLAlchemy

def UserFromDB(username):
    user = classes.User.query.filter_by(username=username).first()
    return user

def test_db_existence():
    """
    Check whether the __init__ created a db and user class table.
    """
    db = SQLAlchemy()
    engine = db.create_engine(Config.SQLALCHEMY_DATABASE_URI, {})
    inspect = db.inspect(engine)
    assert (inspect.has_table("user"))

def test_UserFromDB():
    """
    Assuming that "danny, danny@gmail.com, 1234" is always in the database
    Good to have a test user account
    """
    assert UserFromDB("danny").email == "danny@gmail.com"
    assert UserFromDB("danny").username == "danny"