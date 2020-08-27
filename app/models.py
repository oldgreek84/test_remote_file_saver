import datetime
from mongoengine.errors import NotUniqueError
from werkzeug.security import check_password_hash, generate_password_hash
from uuid import uuid4
from mongoengine import (
        Document, StringField, ReferenceField, DateTimeField, DictField
        )


class User(Document):
    username = StringField(max_length=20, required=True, unique=True)
    password = StringField(max_length=200, required=True)

    
    def __repr__(self):
        return f'<User: {self.username}>'

    def generate_password(self):
        self.password = generate_password_hash(self.password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def save(self):
        try:
            self.generate_password()
            super().save()
        except NotUniqueError:
            print('not unique name')


class FilesStorage(Document):
    key = StringField(required=True)
    created = DateTimeField(default=datetime.datetime.now(), required=True)
    path_to_load = StringField(required=True)
    meta_data = DictField()
    author = ReferenceField(User) 

    def generate_key(self):
        self.key = str(uuid4())


    def save(self):
        try:
            self.generate_key()
            super().save()
        except Exception as e:
            raise e
