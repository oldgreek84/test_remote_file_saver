import dropbox

from flask import Flask

from config import Config
from saver_class import DropboxSaver
from mongoengine import connect, get_db


app = Flask(__name__)
app.config.from_object(Config)

connect(app.config['DB_NAME'])
db = get_db()

dbx = dropbox.Dropbox(app.config['DROPBOX_API'])
obj_saver = DropboxSaver(dbx)

from views import *

if __name__ == "__main__":
    app.run()
