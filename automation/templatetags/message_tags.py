from django import template

register = template.Library()

@register.filter
def is_read_by(message, user):
    print(22)
    print(message.read_logs.filter(owner=user).exists())
    return message.read_logs.filter(owner=user).exists()