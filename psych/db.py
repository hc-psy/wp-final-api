import bson

from flask import current_app, g
from werkzeug.local import LocalProxy
from flask_pymongo import PyMongo

from pymongo.errors import DuplicateKeyError, OperationFailure
from bson.objectid import ObjectId
from bson.errors import InvalidId

from psych.data import DISORDERS

def get_db():
    """
    Configuration method to return db instance
    """
    db = getattr(g, "_database", None)
    
    if db is None:
        db = g._database = PyMongo(current_app).db
        
    return db


# Use LocalProxy to read the global db instance with just `db`
db = LocalProxy(get_db)

def disorders_init():
    db.disorders.delete_many({})
    db.disorders.insert_many(DISORDERS)
    
def get_level_1_disorder(disorder_name):
    myquery = { 'level_1_name': disorder_name }
    return list(db.disorders.find(myquery))

def get_all_disorders():
    return list(db.disorders.find({}))