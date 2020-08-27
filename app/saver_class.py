import os
import dropbox
from abc import ABC, abstractmethod, abstractproperty
from config import BASE_DIR


class WrongLinkValueError(Exception):
    pass


class BaseSaver(ABC):
    @abstractmethod
    def upload(self):
        pass

    @abstractmethod
    def download(self):
        pass


class DropboxSaver(BaseSaver):
    def __init__(self, worker):
        self.worker = worker

    def upload(self, filename, data):
        path_to_file = f'/{filename}'
        try:
            meta_data = self.worker.files_alpha_upload(data, path_to_file)
        except:
            return 
        return meta_data

    def download(self, link):
        try:
            meta, response = self.worker.files_download(link)
        except dropbox.stone_validators.ValidationError:
            raise WrongLinkValueError
        if response.status_code == 200:
            res = response.content
        else:
            res = None
        return res

    def download_to_file(self, filename, dbx_file_path):
        path_to_save = os.path.join(BASE_DIR, filename)
        self.worker.files_download_to_file(path_to_save, dbx_file_path)


class LocalSaver(BaseSaver):
    upload_dir = BASE_DIR + '/uploads'

    def __init__(self):
        pass

    def upload(self, filename, data):
        res = {}
        print('hello')
        if not os.path.exists(self.upload_dir):
            print('make dir')
            os.mkdir(self.upload_dir)
            
        with open(os.path.join(self.upload_dir, filename), 'wb') as f:
            f.write(data)
        res['path_display'] = '/' + filename 
        return res

    def download(self, link):
        with open(self.upload_dir + link, 'rb') as f:
            data = f.read()
        return data


if __name__ == "__main__":
    saver = LocalSaver()
    data = open('/home/doc/1.pdf', 'rb').read()
    from app import uniq_name 
    filename = uniq_name('1.pdf')
    link = '/1d95d2b2-d8ea-40ba-9604-83cc29a9ec67_1.pdf'
