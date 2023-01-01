from flask import Blueprint, request, jsonify
from psych.db import (get_disorders, 
                      create_account, 
                      login_check, 
                      get_therapists, 
                      update_therapist_info,
                      find_possible_disorder_therapists)

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
        code = login_check(username=username, password=password)
        if code == 0:
            message = 'SUCCESS_LOGIN'
        elif code == 1:
            message = 'WRONG_PASSWORD'
        elif code == 2:
            message = 'ACCOUNT_DOESNT_EXIST'
    else:
        message = 'PARAM_ERROR'
        code = 3

    response = {
        'message': message,
        'code': code
    }

    return jsonify(response)


@psych_api.route('/therapists/categories/', methods=['GET'])
def api_get_therapists():

    category = request.args.get('category')
    response = get_therapists(category=category)

    return jsonify(response)


@psych_api.route('/therapists/info/', methods=['PUT'])
def api_update_therapist():

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
        code = update_therapist_info(username=username, req_body=req_body)
        if code == 0:
            message = 'SUCCESS_UPDATE'
        elif code == 2:
            message = 'ACCOUNT_DOESNT_EXIST_OR_NOT_THERAPIST'

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