from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import messages

from django.contrib.auth.models import User

# If user logs in - Success message
@receiver(user_logged_in)
def post_login(sender, user, request, **kwargs):
    messages.add_message(request, messages.SUCCESS, 'You have uccesfully logged in!')


# If user logs out - Success message
@receiver(user_logged_out)
def post_logout(sender, user, request, **kwargs):
    messages.add_message(request, messages.SUCCESS, 'You have succesfully logged out!')


# If user fails to log in - Error message
@receiver(user_login_failed, sender = User)
def failed_login(sender, user, request, **kwargs):
    messages.add_message(request, messages.ERROR, 'Logging in failed!')


# If user signs up - Success message
# @receiver(post_save, sender=User)
# def created_new_user(sender, request, **kwargs):
#     messages.add_message(request, messages.SUCCESS, 'You succesfully created a new account!')