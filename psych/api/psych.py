from flask import Blueprint, request, jsonify
from psych.db import get_level_1_disorder, get_all_disorders

from flask_cors import CORS
from psych.api.utils import expect
from datetime import datetime


psych_api = Blueprint(
    'psych_api', 'psych_api', url_prefix='/api/')

CORS(psych_api)

@psych_api.route('/disorders/', methods=['GET'])
def api_get_level_1_disorder():
    response = get_level_1_disorder(disorder_name=request.args.get('lvl_1_disorder'))
    return jsonify(response)

@psych_api.route('/disorders/allDisorders', methods=['GET'])
def api_get_all_disorders():
    response = get_all_disorders()
    return jsonify(response)