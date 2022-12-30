import bson

from flask import current_app, g
from werkzeug.local import LocalProxy
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt

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

flask_bcrypt = Bcrypt()


def disorders_init():
    db.disorders.delete_many({})
    db.disorders.insert_many(DISORDERS)
    
def get_disorders(disorder_name):
    if disorder_name:
        return list(db.disorders.find({ 'level_1_name': disorder_name }))
    
    return list(db.disorders.find({}))

def create_account(username, password, identity, name, email):
    account = db.accounts.find_one({ 'username': username })
    if account:
        return False
    
    password_hash = flask_bcrypt.generate_password_hash(password).decode('utf-8')
    
    account = {
        'username': username,
        'password': password_hash,
        'identity': identity,
        'name': name, 
        'email': email
    }
    
    db.accounts.insert_one(account)
    return True

def login_check(username, password):
    account = db.accounts.find_one({ 'username': username })
    
    if not account:
        return 2
    
    if not flask_bcrypt.check_password_hash(account['password'], password):
        return 1
    
    return 0
    
    

