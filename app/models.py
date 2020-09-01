import datetime
from uuid import uuid4

from werkzeug.security import check_password_hash, generate_password_hash
from mongoengine.errors import NotUniqueError
from mongoengine import (
        Document, StringField, ReferenceField, DateTimeField, DictField
        )


class NotUniqueUserName(Exception):
    '''
    exception raised if new user name is already exists
    '''


class User(Document):
    '''
    class create User model entry in MongoDb.
    Has entry username its name of the user,
    and entry password hash of new user
    '''

    username = StringField(max_length=20, required=True, unique=True)
    password = StringField(max_length=200, required=True)

    def __repr__(self):
        return f'<User: {self.username}>'

    def generate_password(self):
        '''
        method create user password hash
        '''

        self.password = generate_password_hash(self.password)

    def check_password(self, password):
        '''
        method return bool for cheking user password
        '''
        return check_password_hash(self.password, password)

    def save(self):
        '''
        method generate password before saved user model entry
        '''

        try:
            self.generate_password()
            super().save()
        except NotUniqueError:
            raise NotUniqueUserName('not unique name')


class FilesStorage(Document):
    '''
    class create file storage model for entrt in MongoDb.
    Model saved unique key of uploaded files, loasded date, path for upload
    the file and realation entry author to the user
    '''

    uniq_file_key = StringField(required=True)
    created = DateTimeField(default=datetime.datetime.now(), required=True)
    path_to_load = StringField(required=True)
    meta_data = DictField()
    author = ReferenceField(User)

    def generate_key(self):
        '''
        method create unique key for file entry
        '''

        self.uniq_file_key = str(uuid4())

    def save(self):
        '''
        method generate key before saved file model entry
        '''

        try:
            self.generate_key()
            super().save()
        except Exception as e:
            raise e
