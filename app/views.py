import json
from datetime import datetime, timedelta

import jwt
from flask import jsonify, request, abort, make_response
from mongoengine import NotUniqueError

from app import app, obj_saver
from utils import set_meta, uniq_name, base64_encoding, token_requered
from models import User, FilesStorage
from saver_class import WrongLinkValueError


@app.errorhandler(405)
def not_allowed(error):
    return make_response(jsonify({'error': 'Method not allowed'}), 405)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


@app.route('/api/auth/users/', methods=['GET'])
def save_user():
    if not request.headers:
        abort(400)
    username = request.headers.get('username')
    password = request.headers.get('password')
    user = User(username=username, password=password)
    try:
        user.save()
    except NotUniqueError:
        message = {'status': 'Error', 'message': 'Not unique user name'}
    message = {'status': 'Ok', 'message': 'User saved'}
    return jsonify(message)


@app.route('/api/auth/token/', methods=['POST'])
def get_token():
    if not request.headers:
        abort(400)
    username = request.headers.get('username')
    password = request.headers.get('password')
    user = User.objects.get(username=username)

    if not user:
        abort(400)
    if user.check_password(password):
        payload = {
            'username': username,
            'password': password,
            'exp': datetime.now() + timedelta(minutes=30)
                }
        token = jwt.encode(payload, app.config['SECRET_KEY'])
    else:
        message = {'status': 'error', 'message': 'invalid user data'}
        return jsonify(message)
    return jsonify({'status': 'Ok',
                    'Token': token.decode(app.config['ENCODING'])})


@app.route('/api/values/all/', methods=['GET'])
@token_requered
def get_all(current_user):
    value = FilesStorage.objects.all().to_json()
    return jsonify({'values': json.loads(value)})


@app.route('/api/values/data/', methods=['GET'])
@token_requered
def get_entry_data(current_user):
    if not request.json:
        abort(400)
    key = request.json.get('key')
    data = FilesStorage.objects.get(key=key).to_json()
    return jsonify({'value': [data]})


@app.route('/api/values/', methods=['GET'])
@token_requered
def get_value(currnet_user):
    if not request.json:
        abort(400)
    key = request.json.get('key')
    value = FilesStorage.objects.get(key=key)
    # print(value)
    link_to_dowload = value['path_to_load']
    try:
        data_raw = obj_saver.download(link_to_dowload)
    except WrongLinkValueError:
        abort(400)
    return jsonify({'status': 'ok',
                    'base64_data': base64_encoding(data_raw)})


@app.route('/api/values/', methods=['POST'])
@token_requered
def put_value(current_user):
    if request.files:
        file = request.files.get('file')
        filename = uniq_name(file.filename)
        stream = file.stream
        data = stream.read()
        meta = obj_saver.upload(filename, data)

        if meta:
            meta_dict = set_meta(meta)
            path_to_load = meta_dict['path_display']
            file = FilesStorage(
                path_to_load=path_to_load,
                author=current_user,
                meta_data=meta_dict)
            try:
                file.save()
            except:
                print('file not saved')
        else:
            abort(400)
        stream.close()
        return jsonify({'status': 'OK', 'key': file.key}), 201

    print('not files')
    error = 'Not loading files'
    return jsonify({'status': 'Error', 'error': error})
