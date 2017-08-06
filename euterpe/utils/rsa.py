import binascii

from Crypto.PublicKey import RSA


def encrypt(plain: bytes, modulus: int, exponent: int):
    cipher = RSA.construct((modulus, exponent))
    encrypted = cipher.encrypt(plain, 1)[0]
    return binascii.hexlify(encrypted) 
