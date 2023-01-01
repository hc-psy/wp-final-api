from flask import Blueprint, request, jsonify
from psych.db import (get_disorders,
                      create_account,
                      login_check,
                      get_therapists,
                      get_info,
                      update_info,
                      find_possible_disorder_therapists,
                      create_appointment,
                      get_appointments,
                      update_appointment)

from flask_cors import CORS
from psych.api.utils import expect
from datetime import datetime


psych_api = Blueprint(
    'psych_api', 'psych_api', url_prefix='/api/')

CORS(psych_api)


@psych_api.route('/disorders/', methods=['GET'])
def api_get_disorders():

    disorder = request.args.get('disorder')
    response = get_disorders(disorder_name=disorder)

    return jsonify(response)


@psych_api.route('/signup/', methods=['POST'])
def api_post_signup():

    username = request.get_json(force=True).get('username')
    password = request.get_json(force=True).get('password')
    identity = request.get_json(force=True).get('identity')
    name = request.get_json(force=True).get('name')
    email = request.get_json(force=True).get('email')

    if username and password and (identity in ['therapist', 'client']) and name and email:
        is_success = create_account(username=username,
                                    password=password,
                                    identity=identity,
                                    name=name,
                                    email=email)
        if is_success:
            message = 'SUCCESS_ACCOUNT_CREATION'
            code = 0
        else:
            message = 'ACCOUNT_EXIST'
            code = 1
    else:
        message = 'PARAM_ERROR'
        code = 2

    response = {
        'message': message,
        'code': code
    }

    return jsonify(response)


@psych_api.route('/login/', methods=['POST'])
def api_post_login():

    username = request.get_json(force=True).get('username')
    password = request.get_json(force=True).get('password')

    if username and password:
        code, got_username, got_name, got_identity = login_check(
            username=username, password=password)
        if code == 0:
            message = 'SUCCESS_LOGIN'
        elif code == 1:
            message = 'WRONG_PASSWORD'
        elif code == 2:
            message = 'ACCOUNT_DOESNT_EXIST'
    else:
        message = 'PARAM_ERROR'
        code = 3
        got_username, got_name, got_identity = '', '', ''

    response = {
        'message': message,
        'code': code,
        'username': got_username,
        'name': got_name,
        'identity': got_identity
    }

    return jsonify(response)


@psych_api.route('/accounts/therapists/categories/', methods=['GET'])
def api_get_categories():

    category = request.args.get('category')
    response = get_therapists(category=category)

    return jsonify(response)


@psych_api.route('/accounts/getinfo/', methods=['GET'])
def api_get_info():

    username = request.args.get('username')
    response = get_info(username=username)

    return jsonify(response)


@psych_api.route('/accounts/updateinfo/', methods=['PUT'])
def api_put_updateinfo():

    eligible = True
    for key in request.get_json(force=True).keys():
        if key not in ['username', 'password', 'available_time', 'avatar', 'introduction', 'disorder_categories', 'experiences', 'email']:
            eligible = False

    username = request.get_json(force=True).get('username')

    if not eligible or not username:
        message = 'PARAM_ERROR'
        code = 1
    else:
        req_body = request.get_json(force=True)
        code = update_info(username=username, req_body=req_body)
        if code == 0:
            message = 'SUCCESS_UPDATE'
        elif code == 2:
            message = 'ACCOUNT_DOESNT_EXIST'

    response = {
        'message': message,
        'code': code
    }

    return jsonify(response)


@psych_api.route('/search/', methods=['POST'])
def api_post_search():

    symptoms = request.get_json(force=True).get('symptoms')

    if not symptoms or not isinstance(symptoms, list):
        category, therapists = '', []
        message = 'PARAM_ERROR'
        code = 1
    else:
        category, therapists = find_possible_disorder_therapists(symptoms)
        message = 'SUCCESS_SEARCH'
        code = 0

    response = {
        'category': category,
        'therapists': therapists,
        'message': message,
        'code': code
    }

    return jsonify(response)

@psych_api.route('/appointments/create/', methods=['POST'])
def api_post_appointment_create():

    therapist = request.get_json(force=True).get('therapist')
    client = request.get_json(force=True).get('client')
    time = request.get_json(force=True).get('time')
    meeting_code = request.get_json(force=True).get('meeting_code')

    if therapist and client and time and meeting_code:
        is_success = create_appointment(
            therapist=therapist,
            client=client,
            time=time,
            meeting_code=meeting_code
        )
        if is_success:
            message = 'SUCCESS_APPOINTMENT_CREATION'
            code = 0
        else:
            message = 'APPOINTMENT_EXIST'
            code = 1
    else:
        message = 'PARAM_ERROR'
        code = 2

    response = {
        'message': message,
        'code': code
    }

    return jsonify(response)

@psych_api.route('/appointments/get/', methods=['GET'])
def api_post_appointment_get():
    
    req_body = request.args.to_dict()
    eligible = True
    
    for key in req_body.keys():
        if key not in ['therapist', 'client']:
            eligible = False
            
    if len(list(req_body.keys())) >= 3 or len(list(req_body.keys())) <= 0:
        eligible = False
    
    if not eligible:
        response = {
            'appointments': [],
            'message': 'PARAM_ERROR',
            'code': 1
        }
    else:
        appointments = get_appointments(req_body)
        response = {
            'appointments': appointments,
            'message': 'GET_RESULTS',
            'code': 0
        }
    
    return jsonify(response)

@psych_api.route('/appointments/update/', methods=['PUT'])
def api_post_appointment_put():
    
    therapist = request.get_json(force=True).get('therapist')
    client = request.get_json(force=True).get('client')
    time = request.get_json(force=True).get('time')
    
    eligible = True
    for key in request.get_json(force=True).keys():
        if key not in ['therapist', 'client', 'meeting_code', 'time', 'rating', 'comment', 'status']:
            eligible = False
    
    if not eligible or not therapist or not client or not time:
        message = 'PARAM_ERROR'
        code = 1
    else:
        req_body = request.get_json(force=True)
        code = update_appointment(therapist=therapist, client=client, time=time, req_body=req_body)
        if code == 0:
            message = 'SUCCESS_UPDATE'
        elif code == 2:
            message = 'APPOINTMENT_DOESNT_EXIST'
        elif code == 3:
            message = 'STATUS_STRING_ERROR'

    response = {
        'message': message,
        'code': code
    }

    return jsonify(response)