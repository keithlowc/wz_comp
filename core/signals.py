from django.db.models.signals import m2m_changed, pre_save, post_save, pre_init
from django.dispatch import receiver
from django.contrib import messages
import django.dispatch
from django.contrib.auth.models import User

import requests

send_message = django.dispatch.Signal(providing_args = ['message', 'request', 'type'])

@receiver(send_message)
def send_message_signal(sender, request, **kwargs):
    '''
    This signal works as the
    notification system on the site.
    '''

    message = kwargs['message']
    message_type = kwargs['type']
    
    if message_type == 'ERROR':
        messages.add_message(request, messages.ERROR, message)

    elif message_type == 'SUCCESS':
        messages.add_message(request, messages.SUCCESS, message)

    elif message_type == 'INFO':
        messages.add_message(request, messages.INFO, message)

    elif message_type == 'WARNING':
        messages.add_message(request, messages.WARNING, message)

    elif message_type == 'DANGER':
        messages.add_message(request, messages.DANGER, message)
    

