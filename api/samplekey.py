from cryptography.fernet import Fernet
from django.conf import settings
import hashlib
import base64




def encrypt(val):
    string = bytes(val, 'utf-8')
    cipher_suite = Fernet(settings.ID_ENCRYPTION_KEY)
    cipher_text = cipher_suite.encrypt(string)
    return val

def encrypt2(val):
    string = bytes(val, 'utf-8')
    cipher_suite = Fernet(settings.ID_ENCRYPTION_KEY)
    cipher_text = cipher_suite.encrypt(string)
    return cipher_text


def decrypt(val):
    addlbl =val
    val = str(val)
    cipher_suite = Fernet(settings.ID_ENCRYPTION_KEY)

    val = val.replace("b'", '')
    val = val.replace("'", '')
    val = bytes(val, 'utf-8')
    try:
        plain_text = cipher_suite.decrypt(val).decode('utf-8')
    except:
        plain_text = addlbl



    return plain_text
