from flask import Blueprint, request, jsonify
from psych.db import get_disorders, create_account, login_check

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
    
    username = request.args.get('username')
    password = request.args.get('password')
    identity = request.args.get('identity')
    name = request.args.get('name')
    email = request.args.get('email')
    
    if username and password and identity and name and email:
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
    
    username = request.args.get('username')
    password = request.args.get('password')
    
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