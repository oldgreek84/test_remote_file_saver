from datetime import datetime, timedelta
import jwt

from mongoengine.errors import DoesNotExist

from app import app, obj_saver
from utils import set_uniq_name, encode_to_base64
from models import User, FilesStorage, NotUniqueUserName
from saver_class import WrongLinkValueError


def create_new_user(username, password):
    ''' creates a new user entry in the database '''

    try:
        User(username=username, password=password).save()
    except NotUniqueUserName:
        return {'status': 'Error', 'message': 'Not unique user name'}
    return {'status': 'Ok', 'message': 'User saved success'}


def get_user_token(username, password):
    ''' checkes username and password  and returns
    sting auth token for user
    '''

    if check_user(username, password):
        return create_user_token(username, password)
    return None


def check_user(username, password):
    ''' checks the user username and password from the database '''

    try:
        user = User.objects.get(username=username)
    except DoesNotExist:
        return False
    return user.check_password(password)


def create_user_token(username, password):
    ''' generates new string token for the current user '''

    payload = {
        'username': username,
        'password': password,
        'exp': datetime.now() + timedelta(minutes=30)}
    return jwt.encode(payload, app.config['SECRET_KEY'])


def download_file_from_service(uniq_file_key):
    ''' downloads file data from remote service in string base64 coding '''

    try:
        data_raw = obj_saver.download(get_download_file_link(uniq_file_key))
    except WrongLinkValueError:
        return None, 'wrong link to file'
    return encode_to_base64(data_raw), None


def get_download_file_link(uniq_file_key):
    ''' finds file entry in the database returns
    string path to upload file
    '''

    file_data = FilesStorage.objects.get(uniq_file_key=uniq_file_key)
    return file_data.path_to_load


def save_file_data(author, file_data_object):
    ''' saves a file to our server and return string
    unique string key
    '''

    try:
        meta_data = save_file_data_to_service(
            filename=set_uniq_name(file_data_object.filename),
            data_bytes=read_file_stream(file_data_object))

        try:
            uniq_file_key = save_file_data_to_db(
                author=author,
                path_to_load=meta_data.get('path_display'),
                meta_data=meta_data)
        except Exception:
            return None, 'file not save to db'
    except Exception:
        return None, 'file not saved to server'
    return uniq_file_key, None


def save_file_data_to_service(filename, data_bytes):
    ''' saves a file bytes data to remote service and
    returns dict with file info
    '''

    meta_data = obj_saver.upload(filename, data_bytes)
    return meta_data


def save_file_data_to_db(author, path_to_load, meta_data):
    ''' saves a file entry to the database and
    returns a unique string key
    '''

    file = FilesStorage(
        path_to_load=path_to_load,
        author=author,
        meta_data=meta_data)
    file.save()
    return file.uniq_file_key


def read_file_stream(file_object):
    ''' reads a special file object with attributes:
    obj.stream: file io wrapper object
    obj.filename: string file name
    and returns bytes data from the object
    '''

    with file_object.stream as opened_file_object:
        bytes_data = opened_file_object.read()
    return bytes_data
