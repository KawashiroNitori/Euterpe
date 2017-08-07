from Crypto.Cipher import AES


def encrypt(plain: bytes, key: bytes, iv: bytes):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padding = 16 - len(plain) % 16
    data = plain + (padding * chr(padding)).encode('utf8')
    encrypted = cipher.encrypt(data)
    return encrypted
