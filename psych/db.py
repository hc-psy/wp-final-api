import bson

from flask import current_app, g
from werkzeug.local import LocalProxy
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt

from pymongo.errors import DuplicateKeyError, OperationFailure
from bson.objectid import ObjectId
from bson.errors import InvalidId

from psych.data import DISORDERS, ACCOUNTS


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


def accounts_init():
    db.accounts.delete_many({})
    for obj in ACCOUNTS:
        create_account(
            username=obj['username'],
            password=obj['password'],
            identity=obj['identity'],
            name=obj['name'],
            email=obj['email'],
            avatar=obj['avatar'],
            disorder_categories=obj['disorder_categories'],
            available_time=obj['available_time'],
            experiences=obj['experiences'])


def get_disorders(disorder_name):
    if disorder_name:
        return list(db.disorders.find({'level_1_name': disorder_name}))

    return list(db.disorders.find({}))


def create_account(username,
                   password,
                   identity,
                   name,
                   email,
                   avatar='',
                   disorder_categories=[],
                   introduction='',
                   available_time=[],
                   experiences=[]):

    account = db.accounts.find_one({'username': username})
    if account:
        return False

    password_hash = flask_bcrypt.generate_password_hash(
        password).decode('utf-8')

    account = {
        'username': username,
        'password': password_hash,
        'identity': identity,
        'name': name,
        'email': email,
        'avatar': avatar,
        'disorder_categories': disorder_categories,
        'introduction': introduction,
        'available_time': available_time,
        'experiences': experiences
    }

    db.accounts.insert_one(account)
    return True


def login_check(username, password):
    account = db.accounts.find_one({'username': username})

    if not account:
        return 2, '', '', ''

    if not flask_bcrypt.check_password_hash(account['password'], password):
        return 1, '', '', ''

    return 0, account['username'], account['name'], account['identity']


def get_therapists(category):
    if category:
        therapists = db.accounts.find({'identity': 'therapist', 'disorder_categories': category}, {
                                      '_id': 0, 'password': 0, 'identity': 0})
    else:
        therapists = db.accounts.find({'identity': 'therapist'}, {
                                      '_id': 0, 'password': 0, 'identity': 0})

    return list(therapists)


def get_info(username):
    if username:
        info = db.accounts.find_one({'username': username}, {
            '_id': 0, 'password': 0})
        if info:
            response = {
                'info': info,
                'message': 'SUCCESS_GET',
                'code': 0
            }
        else:
            response = {
                'info': {},
                'message': 'ACCOUNT_DOESNT_EXIST',
                'code': 1
            }
    else:
        response = {
            'info': {},
            'message': 'PARAM_ERROR',
            'code': 2
        }

    return response


def update_info(username, req_body):
    account = db.accounts.find_one(
        {'username': username})

    if not account:
        return 2

    if 'password' in list(req_body.keys()):

        password_hash = flask_bcrypt.generate_password_hash(
            req_body['password']).decode('utf-8')

        req_body.pop('password', None)
        req_body = {**req_body, 'password': password_hash}

    db.accounts.update_one(
        {'username': username}, {'$set': req_body})

    return 0


def find_possible_disorder_therapists(symptoms):
    disorders = db.disorders.find({})

    match_num = -1
    target_category = ''
    for i in disorders:
        for j in i['level_2']:
            current_match_num = len(list(set(symptoms).intersection(
                set(j['symptoms'])))) / len(j['symptoms'])
            if current_match_num >= match_num:
                match_num = current_match_num
                target_category = i['level_1_name']

    return target_category, list(db.accounts.find({'identity': 'therapist', 'disorder_categories': target_category}, {'_id': 0, 'password': 0, 'identity': 0}))


def create_appointment(therapist,
                       client,
                       time,
                       meeting_code,
                       rating=-1,
                       comment="",
                       status='ACTIVE'):

    appointment = db.appointments.find_one(
        {'therapist': therapist, 'client': client, 'time': time})
    if appointment:
        return False

    appointment = {
        'therapist': therapist,
        'client': client,
        'meeting_code': meeting_code,
        'time': time,
        'rating': rating,
        'comment': comment,
        'status': status
    }

    db.appointments.insert_one(appointment)
    return True


def get_appointments(req_body):

    appointments = list(db.appointments.find(req_body))

    return appointments

def update_appointment(therapist, client, time, req_body):
    appointment = db.appointments.find_one(
        {'therapist': therapist, 'client': client, 'time': time})

    if not appointment:
        return 2

    if 'status' in list(req_body.keys()):
        if req_body['status'] not in ['ACTIVE', 'UNCOMMENTED', 'COMMENTED']:
            return 3

    db.appointments.update_one(
        {'therapist': therapist, 'client': client, 'time': time}, {'$set': req_body})

    return 0