from django import template

import ast

from datetime import timedelta

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if key == 'kd':
        return '{:.2f}'.format(dictionary.get(key))
    else:
        return dictionary.get(key)

@register.filter
def add(index):
    return index + 1


@register.filter
def format_kd(kd):
    kd = str(kd).replace(',','.')
    return '{:.2f}'.format(float(kd))
            

@register.filter
def remove_everything_after_hashtag(user):
    return user.split('#')[0]


@register.filter
def convert_days_to_epoch(days):
    return timedelta(days = days).total_seconds()


@register.filter
def convert_plus_to_empty(string):
    return string.replace('+',' ')

@register.filter
def convert_hash_to_web_friendly(string):
    return string.replace('#','%23')

@register.filter
def youtube_embed_url_fixer(string):
    return string.replace('watch?v=','embed/')

@register.filter
def convert_seconds_to_minutes(seconds):
    return int(seconds / 60)