import json
import random
import string
import base64
import binascii
from urllib.parse import urljoin

import requests

from euterpe.utils import aes
from euterpe.utils import rsa
from euterpe import errors


class BaseAPI(object):
    def __init__(self):
        self.session = requests.Session()

    def get(self, url):
        return self.session.get(url)

    def post(self, url, data):
        return self.session.post(url, data)


class NeteaseMusicAPI(BaseAPI):
    RSA_E = 0x010001
    RSA_N = 0x00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7
    AES_FIRST_KEY = b'0CoJUm6Qyw8W8jud'
    AES_IV = b'0102030405060708'
    BASE_URL = 'http://music.163.com'

    def __init__(self):
        super(NeteaseMusicAPI, self).__init__()

    def encrypt_body(self, plain_text: str, key: bytes):
        first_cipher = aes.encrypt(plain_text.encode('utf8'), self.AES_FIRST_KEY, self.AES_IV)
        first_cipher = base64.b64encode(first_cipher)
        result_cipher = aes.encrypt(first_cipher, key, self.AES_IV)
        return base64.b64encode(result_cipher)

    def encrypt_key(self, plain_key: bytes):
        result = rsa.encrypt(plain_key[::-1], self.RSA_N, self.RSA_E)
        return binascii.hexlify(result)

    def get(self, url: str):
        url = urljoin(self.BASE_URL, url)
        return self.session.get(url)

    def post(self, url: str, data, key: bytes=None):
        url = urljoin(self.BASE_URL, url)
        if not key:
            key = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16)).encode()
        if isinstance(data, dict):
            data = json.dumps(data)
        sending_data = {'params': self.encrypt_body(data, key), 'encSecKey': self.encrypt_key(key)}
        return self.session.post(url, sending_data)

    def get_song_detail(self, song_id: int):
        url = '/weapi/v3/song/detail'
        data = {'id': str(song_id), 'c': json.dumps([{'id': str(song_id)}])}
        return self.post(url, data).json()

    def get_playlist_detail(self, playlist_id: int):
        url = '/weapi/v3/playlist/detail'
        data = {'id': str(playlist_id)}
        return self.post(url, data).json()

    def get_song_audio(self, song_id):
        url = '/weapi/song/enhance/player/url'
        if isinstance(song_id, int):
            song_ids = [song_id]
        else:
            song_ids = song_id
        data = {'br': 128000, 'ids': song_ids}
        return self.post(url, data).json()

    def get_song_file(self, song_id):
        info = self.get_song_audio(song_id)
        try:
            url = info['data'][0]['url']
        except KeyError:
            raise errors.SongNotFoundError()
        if not url:
            raise errors.SongCannotDownloadError()
        content = self.session.get(url).content
        return content


if __name__ == '__main__':
    api = NeteaseMusicAPI()
    res = api.get_song_file(27632615)
    with open('temp.mp3', 'wb') as file:
        file.write(res)
    # print(json.dumps(res, indent=2))
