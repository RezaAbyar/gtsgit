from django import template
import hashlib
import base64
from api.samplekey import encrypt2 as Encrypt,decrypt as Decrypt

register = template.Library()


@register.filter
def to_md5(value):
    _value = Encrypt(str(value))
    return _value


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def split(value, arg):
    return value.split(arg)

