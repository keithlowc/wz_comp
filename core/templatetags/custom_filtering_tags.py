from django import template
import ast

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
def remove_everything_after_hashtag(user):
    return user.split('#')[0]
