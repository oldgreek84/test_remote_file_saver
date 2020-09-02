from functools import wraps
from uuid import uuid4
from base64 import b64encode
import traceback

import jwt
from flask import request, jsonify

from app import app
from models import User


def json_response(message, code=200):
    ''' creates a json object response '''

    return jsonify(message), code


def error_response(exception):
    ''' createa response for all exceptions in app json view '''

    res = {
        'status': 'error',
        'message': str(exception),
        'traceback_info': traceback.print_exc()}
    return json_response(res, 400)


def exception_catcher(func_to_decor):
    ''' decorator cathes all exceptions on base level views '''

    @wraps(func_to_decor)
    def wrapper(*args, **kwargs):
        try:
            return func_to_decor(*args, **kwargs)
        except Exception as e:
            return error_response(e)
    return wrapper


def token_requered(func_to_decor):
    '''
    decorator checks a user data token and returns the current user
    '''

    @wraps(func_to_decor)
    def wrapper(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if token:
            try:
                data = jwt.decode(token, app.config['SECRET_KEY'])
                user = User.objects.get(username=data['username'])
                current_user = user
                return func_to_decor(current_user, *args, **kwargs)
            except jwt.exceptions.ExpiredSignatureError:
                message = {
                    'status': 'Error',
                    'message': 'Token has expired'}
            except jwt.exceptions.DecodeError:
                message = {
                    'status': 'Error',
                    'message': 'Invalid token'}
        else:
            message = {
                'status': 'Error',
                'message': 'Token is required'}
        return jsonify(message), 401
    return wrapper


def set_uniq_name(filename):
    ''' creates a unique name of filename and returns it '''

    return f'{str(uuid4())}_{filename}'


def encode_to_base64(raw_data):
    '''
    encodes a bytes data to base64 string
    :raw_data: bytes data of file
    return -> decoded string in base64 coding
    '''

    base64_bytes = b64encode(raw_data)
    return base64_bytes.decode(app.config['ENCODING'])
