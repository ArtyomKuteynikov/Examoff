import datetime
import time
# from customer.models import Settings
from django import template

register = template.Library()


@register.simple_tag
def multiply(a, b):
    return a * b


@register.simple_tag
def divide(a, b):
    if not a or not b:
        return 0
    return "{:.2f}".format(float(float(a) / float(b)))


@register.simple_tag
def price(a):
    if not a:
        return ''
    return "{:.2f}".format(float(a))


@register.simple_tag
def price_js(a):
    if not a:
        return ''
    return "{:.8f}".format(float(a))


@register.simple_tag
def minutes(created, time_limit):
    time_limit = time_limit - (int(time.time()) - int(created.timestamp()))
    minutes = time_limit // 60
    return minutes


@register.simple_tag
def seconds(created, time_limit):
    time_limit = time_limit - (int(time.time()) - int(created.timestamp()))
    seconds = time_limit % 60
    return seconds


@register.simple_tag
def all_seconds(created, time_limit):
    time_limit = time_limit - (int(time.time()) - int(created.timestamp()))
    return time_limit


@register.simple_tag
def percent(a, b):
    if not a or not b:
        return 0
    return "{:.2f}".format(float(float(a) / float(b))*100)


@register.simple_tag
def zeros(a):
    if not a:
        return 0
    return round(a, 2)


@register.simple_tag
def time_date(a):
    return a.strftime("%d.%m.%Y")


@register.simple_tag
def time_hours(a, b):
    final = a + datetime.timedelta(hours=abs(b)) if b > 0 else a - datetime.timedelta(hours=abs(b))
    return final.strftime("%H:%M")
