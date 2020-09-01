from flask import jsonify, request, abort, make_response

from app import app
from utils import token_requered, exception_catcher
from services import (
        create_new_user, get_user_token, download_file_from_service,
        save_file_data)


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
@exception_catcher
def save_new_user():
    ''' create new user with rest api request '''

    if not request.headers:
        abort(400)
    username = request.headers.get('username')
    password = request.headers.get('password')
    user_creation_message = create_new_user(username, password)
    return jsonify(user_creation_message)


@app.route('/api/auth/token/', methods=['GET'])
def get_token():
    ''' create string auth token and return it to current user '''

    if not request.headers:
        abort(400)
    username = request.headers.get('username')
    password = request.headers.get('password')
    token = get_user_token(username, password)
    if token:
        message = {
            'status': 'Ok',
            'Token': token.decode(app.config['ENCODING'])}
        status_code = 200
    else:
        message = {'status': 'error', 'message': 'invalid user data'}
        status_code = 400
    return jsonify(message), status_code


@app.route('/api/values/', methods=['GET'])
@token_requered
def get_file_data(currnet_user):
    '''
    func get unique file database key and
    return encoded to base64 file data string
    '''

    if not request.json:
        return jsonify({
            'status': 'error',
            'message': 'not sended unqiue key'}), 400
    uniq_file_key = request.json.get('key')
    base64_file_data, error = download_file_from_service(uniq_file_key)
    if error:
        return jsonify({'status': 'error', 'message': error}), 400
    return jsonify({'status': 'Ok', 'base64_file_data': base64_file_data}), 201


@app.route('/api/values/', methods=['POST'])
@token_requered
def send_file_data(current_user):
    '''
    send opened file data for current user to save it in
    database and return unique key
    '''

    if not request.files:
        return jsonify({'status': 'Error', 'error': 'not files sended'}), 400

    file_data_object = request.files.get('file')
    uniq_file_key, error = save_file_data(current_user,
                                          file_data_object)
    if error:
        return jsonify({'status': 'error', 'message': error}), 400
    return jsonify({'status': 'OK', 'uniq_file_key': uniq_file_key}), 201
