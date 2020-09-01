from datetime import datetime, timedelta
import jwt

from app import app, obj_saver
from utils import set_uniq_name, encode_to_base64
from models import User, FilesStorage, NotUniqueUserName
from saver_class import WrongLinkValueError
from mongoengine.errors import DoesNotExist


def create_new_user(username, password):
    ''' create new user in database '''

    try:
        User(username=username, password=password).save()
    except NotUniqueUserName:
        return {'status': 'Error', 'message': 'Not unique user name'}
    return {'status': 'Ok', 'message': 'User saved success'}


def get_user_token(username, password):
    ''' return sting auth token for user with password and username '''

    if check_user(username, password):
        return create_user_token(username, password)
    return None


def check_user(username, password):
    ''' checking username and password for curren user '''

    try:
        user = User.objects.get(username=username)
    except DoesNotExist:
        return False
    return user.check_password(password)


def create_user_token(username, password):
    '''
    generate new token for current user
    username: str
    password: str
    expiered_time: dict with key-> time param name and value -> int value
    '''

    payload = {
        'username': username,
        'password': password,
        'exp': datetime.now() + timedelta(minutes=30)}
    return jwt.encode(payload, app.config['SECRET_KEY'])


def download_file_from_service(uniq_file_key):
    ''' download file data from remote service in string base64 coding '''

    try:
        data_raw = obj_saver.download(get_download_file_link(uniq_file_key))
    except WrongLinkValueError:
        return None, 'wrong link to file'
    return encode_to_base64(data_raw), None


def get_download_file_link(uniq_file_key):
    ''' return string path to upload file '''

    file_data = FilesStorage.objects.get(uniq_file_key=uniq_file_key)
    return file_data.path_to_load


def save_file_data(author, file_data_object):
    ''' save file to our server and return string unique string key '''

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
    ''' save file bytes data to remote service and return dict
    with file info '''

    meta_data = obj_saver.upload(filename, data_bytes)
    return meta_data


def save_file_data_to_db(author, path_to_load, meta_data):
    ''' save file entry to database and return unique string key '''

    file = FilesStorage(
        path_to_load=path_to_load,
        author=author,
        meta_data=meta_data)
    file.save()
    return file.uniq_file_key


def read_file_stream(file_object):
    ''' read special file object to data bytes stream and
    return this bytes '''

    with file_object.stream as opened_file_object:
        bytes_data = opened_file_object.read()
    return bytes_data
