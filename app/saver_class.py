import os
from abc import ABC, abstractmethod

import dropbox
from config import BASE_DIR
# from utils import get_meta_data_attributes


def get_meta_data_attributes(meta_data):
    '''
    function recieves a object and returns dict with attributes of object
    '''

    res = {}
    attributes = [p for p in dir(meta_data) if not p.startswith('_')]
    for attr in attributes:
        res[attr] = getattr(meta_data, attr)
    return res


class WrongLinkValueError(Exception):
    '''
    Excepltion of wrong link to file from dropbox
    '''


class BaseSaver(ABC):
    '''
    class realise interface for uploads and downloads file
    with some remote service
    '''

    @abstractmethod
    def upload(self, filename, data):
        '''
        method uploads the file to remote server
        :filename: name for saved file
        :data: bytes of file
        return -> string path to download file and dict of file meta data
        '''

    @abstractmethod
    def download(self, link):
        '''
        method downloads the file from remote server
        :link: link for uplaod file
        retun -> bytes data of file
        '''


class DropboxSaver(BaseSaver):
    '''
    class uplaods and downloads the file with dropbox server
    '''

    def __init__(self, worker):
        self._worker = worker

    def upload(self, filename, data):
        '''
        uploads file to remote dropbox server
        returns special link to file and file meta data
        '''
        path_to_file = f'/{filename}'
        try:
            meta_data = self._worker.files_upload(data, path_to_file)
        # except dropbox.stone_validators.ValidationError:
        #     raise WrongLinkValueError('wrong path to file pattern')
        # except TypeError:
        #     return None
        except Exception as e:
            raise e
        return get_meta_data_attributes(meta_data)

    def download(self, link):
        '''
        downloads file data from remote server with special link
        and returns bytes
        '''

        try:
            _, response = self._worker.files_download(link)
        except dropbox.stone_validators.ValidationError:
            raise WrongLinkValueError
        if response.status_code == 200:
            file_data = response.content
        else:
            file_data = None
        return file_data


class LocalSaver(BaseSaver):
    ''' uploads and downloads the file on local server '''

    upload_dir = BASE_DIR + '/uploads'

    def __init__(self):
        pass

    def upload(self, filename, data):
        '''
        uploads file to local dir
        :filename: string file name
        :data: bytes of file
        return -> dict with entry 'path_display' special link to file
        '''

        res = {}
        if not os.path.exists(self.upload_dir):
            os.mkdir(self.upload_dir)

        with open(os.path.join(self.upload_dir, filename), 'wb') as f:
            f.write(data)
        res['path_display'] = '/' + filename
        return res

    def download(self, link):
        '''
        downloads file from local server with special link
        :link: string link to dowload file
        return -> bytes file data
        '''

        with open(self.upload_dir + link, 'rb') as f:
            data = f.read()
        return data


if __name__ == "__main__":
    saver = LocalSaver()
    test_data = open('/home/doc/1.pdf', 'rb').read()
    from utils import set_uniq_name
    test_filename = set_uniq_name('1.pdf')
    TEST_LINK = '/1d95d2b2-d8ea-40ba-9604-83cc29a9ec67_1.pdf'
