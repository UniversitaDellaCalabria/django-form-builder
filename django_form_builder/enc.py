import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from django.conf import settings


_secret = getattr(settings, 'CAPTCHA_SECRET', b'secret')
_salt = getattr(settings, 'CAPTCHA_SALT', b'salt')
_kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
                  length=32,
                  salt=_salt,
                  iterations=100000,
                  backend=default_backend())

key = base64.urlsafe_b64encode(_kdf.derive(_secret))
_encoder = Fernet(key)

def encrypt(text):
    enc_text = _encoder.encrypt(text.encode())
    return enc_text


def decrypt(b64_text):
    text = base64.b64decode(b64_text)
    decrypted = _encoder.decrypt(text)
    return decrypted
