import os
import jwt
from functools import wraps
from uuid import uuid4
from base64 import b64encode, b64decode
from flask import request, jsonify
from app import app
from models import User


def token_requered(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if token:
            try:
                data = jwt.decode(token, app.config['SECRET_KEY'])
                user = User.objects.get(username=data['username'])
                current_user = user
                return f(current_user, *args, **kwargs)
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


def set_meta(meta):
    res = {}
    l = [p for p in dir(meta) if not p.startswith('_')]
    for par in l:
        res[par] = getattr(meta, par)
    return res


def uniq_name(filename):
    return f'{str(uuid4())}_{filename}'


def base64_encoding(raw_data):
    base64_bytes = b64encode(raw_data)
    return base64_bytes.decode(app.config['ENCODING'])


def save_file(filename, data, size=1024):
    with open(filename, 'wb') as f:
        while True:
            
            data = data[:size]
            if not data: break
            print(len(data))
            f.write(data)


def reader(file, size=1024):
    with open(file, 'rb') as data:
        while True:

            line = data.read(size)
            if not line: break
            yield line
            print(len(line))


def saver(data, file_name):
    with open(file_name, 'ab') as f:
        f.write(data)
        print(len(data))


def main_saver(from_file, to_file, buffer_size=1024):
    gen = reader(from_file, buffer_size)
    with open(to_file, 'wb') as f:
        while True:
            try:
                d = next(gen)
                f.write(d)
                print('writing...')
            except StopIteration:
                print('not data')
                break
