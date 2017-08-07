import json
import random
import string
import base64
import binascii
from urllib.parse import urljoin

import requests

from euterpe.utils import aes
from euterpe.utils import rsa


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


if __name__ == '__main__':
    payload = {'s': 'snow halation', 'type': '1', 'offset': '0', 'total': 'true', 'limit': '10'}
    url = '/weapi/cloudsearch/get/web'
    session = NeteaseMusicAPI()
    res = session.post(url, payload)
    print(json.dumps(res.json(), indent=2))
