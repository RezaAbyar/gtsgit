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

@register.filter
def selectattr(seq, attr):
    """فیلتر برای انتخاب ویژگی از یک شیء"""
    return [getattr(item, attr, None) for item in seq]

@register.filter
def select_equalto(seq, value):
    """فیلتر برای مقایسه مقادیر"""
    return [item for item in seq if item == value]