# در فایل templatetags/certificate_filters.py
from django import template
from django.utils.timesince import timesince
import datetime

register = template.Library()

@register.filter
def timeuntil(value, arg):
    """محاسبه فاصله زمانی بین دو تاریخ"""
    try:
        if value and arg:
            return timesince(arg, value)
    except:
        pass
    return ""