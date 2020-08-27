import os


BASE_DIR = os.path.abspath(os.path.curdir)


class Config:
    DEBUG = True
    # os.urandom(28).hex()
    SECRET_KEY = (os.environ.get('SECRET_KEY') or
            '030b3ea5725fcd153cdf53ae4c05033d5ca1597d8ed3b48281b7c180')
    BASE_DIR = os.path.abspath(os.path.curdir)
    DB_NAME = os.environ.get('DB_NAME') or 'test_db'
    ENCODING = 'utf-8'
    DROPBOX_API = (os.environ.get('DROPBOX_API') or
            'nDKFViLdtqgAAAAAAAAAAU3FUTH5J96vS4twxfYsMHG2id5ovZ7Gp2KVembssGxw')
