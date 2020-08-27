import sys
import os
import json
import dropbox
from base64 import b64encode, b64decode
from datetime import datetime
from uuid import uuid4

from flask import Flask, jsonify, request, abort

from db_model import MongodbAPI
from config import Config
from saver_class import DropboxSaver
from mongoengine import connect, get_db


app = Flask(__name__)
app.config.from_object(Config)

connect(app.config['DB_NAME'])
db = get_db()
# db = MongodbAPI(app.config['DB_NAME'])
# db.set_collection('values')

dbx = dropbox.Dropbox(app.config['DROPBOX_API']) 
obj_saver = DropboxSaver(dbx)

from views import *

if __name__ == "__main__":
    app.run()