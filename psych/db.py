from flask import current_app, g
from werkzeug.local import LocalProxy
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_mail import Message
import pandas as pd
import random

from psych.data import DISORDERS, ACCOUNTS, VIDEOS, FAKE_CLIENTS


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


def create_fake_account():
    for obj in FAKE_CLIENTS:
        create_account(
            username=obj['username'],
            password=obj['password'],
            identity=obj['identity'],
            name=obj['name'],
            email=obj['email'],
            avatar="",
            disorder_categories="",
            available_time="",
            experiences="",
            introduction="")


def create_meeting_code():
    string = ''
    for i in range(12):
        chr_type = random.randint(0, 3)
        if i == 3 or i == 8:
            string += '-'
        elif chr_type == 0:
            string += chr(random.randint(65, 90))
        elif chr_type == 1:
            string += chr(random.randint(97, 122))
        else:
            string += str(random.randint(0, 9))
    return string


def create_fake_appointments():
    db.appointments.delete_many({})
    appointment_num = 0
    fake_comments = pd.read_csv("psych/comments.csv", header=None)
    for i in range(3):
        print(f"PROCESSING APPOINTMENTS BACTH {i+1} / 3 ...")
        for thera in ACCOUNTS:
            thera_username = thera['username']
            for client in FAKE_CLIENTS:
                client_username = client['username']
                rating = random.randint(3, 5)
                meeting_code = create_meeting_code()
                date = str(int(appointment_num / 12) + 1).zfill(2)
                hour = str(8 + appointment_num % 12).zfill(2)
                time = f'2022/12/{date}_{hour}'
                create_appointment(thera_username, client_username, time, meeting_code,
                                   rating, fake_comments.iloc[appointment_num][0], 'COMMENTED')
                appointment_num += 1


def appointments_init():
    create_fake_account()
    create_fake_appointments()


def disorders_init():
    db.disorders.delete_many({})
    db.disorders.insert_many(DISORDERS)


def videos_init():
    db.videos.delete_many({})
    db.videos.insert_many(VIDEOS)


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
            experiences=obj['experiences'],
            introduction=obj['introduction'])


def get_disorders(disorder_name):
    if disorder_name:
        return list(db.disorders.find({'level_1_name': disorder_name}))

    return list(db.disorders.find({}))


def get_videos(disorder_name):
    if disorder_name:
        return list(db.videos.find({'disorder': disorder_name}))

    return list(db.videos.find({}))


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


def update_status(machine_time, mail):
    appointments = list(db.appointments.find(
        {'status': 'ACTIVE', 'time': machine_time}))

    if len(appointments) == 0:
        print("NOTHING UPDATED")
        return

    body = {
        'status': 'UNCOMMENTED'
    }

    db.appointments.update_many(
        {'status': 'ACTIVE', 'time': machine_time}, {'$set': body})

    with mail.connect() as conn:
        for obj in appointments:
            therapist = db.accounts.find_one(
                {'username': obj['therapist'], 'identity': 'therapist'})
            client = db.accounts.find_one(
                {'username': obj['client'], 'identity': 'client'})

            therapist_name = therapist['name']
            therapist_mail = therapist['email']
            therapist_subject = f"???BeBetter??? {therapist_name}, ??????????????????????????????"

            client_name = client['name']
            client_mail = client['email']
            client_subject = f"???BeBetter??? {client_name}, ??????????????????????????????"

            therapist_txt = f'''
            ?????????<strong>{therapist_name}</strong>?????????????????????
            <br>
            <br>
            ??????<strong>{client_name}??????</strong>?????????<strong>{machine_time.split('_')[0]}???{machine_time.split('_')[1]}???</strong>??????????????????<strong>?????????</strong>???????????????????????????????????????
            <br>
            <br>
            ??????????????????????????????
            <br>
            <br>
            <img style="height:60px;" src="https://i.imgur.com/88AKnFs.png" />
            <br>
            BeBetter??????
            '''

            client_txt = f'''
            ?????????<strong>{client_name}</strong>??????????????????
            <br>
            <br>
            ??????<strong>{therapist_name}?????????</strong>?????????<b>{machine_time.split('_')[0]}???{machine_time.split('_')[1]}???</strong>??????????????????<strong>?????????</strong>???????????????????????????????????????
            <br>
            <br>
            ??????????????????????????????
            <br>
            <br>
            <img style="height:60px;" src="https://i.imgur.com/88AKnFs.png" />
            <br>
            BeBetter??????
            '''

            msg1 = Message(recipients=[therapist_mail],
                           html=therapist_txt,
                           subject=therapist_subject)

            msg2 = Message(recipients=[client_mail],
                           html=client_txt,
                           subject=client_subject)

            conn.send(msg1)
            conn.send(msg2)

    print("SOME DATA UPDATED AND EMAIL SENT")
