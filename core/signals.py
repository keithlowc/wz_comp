from django.db.models.signals import m2m_changed, pre_save, post_save, pre_init
from django.dispatch import receiver
from django.contrib import messages
import django.dispatch
from django.contrib.auth.models import User

from core.models import Profile, Teams, StaffCustomTeams
from core.warzone_api import WarzoneApi

from warzone_general.settings import headers

import requests

send_message = django.dispatch.Signal(providing_args = ['message', 'request', 'type'])
recalculate_stats_for_team = django.dispatch.Signal(providing_args = ['profiles', 'request', 'team_name'])
recalculate_stats = django.dispatch.Signal(providing_args = ['activision_tag', 'request'])


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


@receiver(recalculate_stats_for_team)
def recalculate_stats_for_team_signal(sender, request, **kwargs):
    '''
    Use this function to
    recalculate all data points
    in the total user 
    '''

    profiles = kwargs['profiles']
    team_name = kwargs['team_name']

    data = {
        'kda': [],
        'wins': [],
        'kills': []
    }

    total_users = len(profiles)

    total_kda = 0

    for profile in profiles:
        user = Profile.objects.get(activision_tag = profile)
        data['kda'].append(user.kda)
        data['wins'].append(user.wins)
        data['kills'].append(user.total_kills)

    total_kda = sum(data['kda']) / total_users
    total_wins = sum(data['wins'])
    total_kills = sum(data['kills'])
    
    team_stats = Teams.objects.get(team_name = team_name)
    team_stats.cummulative_kd = '{:.3f}'.format(total_kda)
    team_stats.total_wins = total_wins
    team_stats.total_kills = total_kills
    team_stats.save()

    messages.add_message(request, messages.SUCCESS, 'Finished recalculating')


@receiver(recalculate_stats)
def recalculate_stats_signal(sender, request, **kwargs):
    '''
    This function allows you
    to refresh your account status
    on submission of activision 
    tag
    '''

    activision_tag = kwargs['activision_tag']

    profile = Profile.objects.filter(activision_tag = activision_tag)

    warzone_api = WarzoneApi(tag = profile[0].activision_tag, 
                            platform = 'acti')

    battle_royale = warzone_api.get_warzone_general_stats()

    try:
        battle_royale = battle_royale['br']

        profile[0].kda = '{:.3f}'.format(battle_royale['kdRatio'])
        profile[0].wins = battle_royale['wins']
        profile[0].total_kills = battle_royale['kills']
        profile[0].save()
    
        messages.add_message(request, messages.SUCCESS, 'Finished adding new tag and re-calculating')
    
    except Exception as e:
        print(e)
        messages.add_message(request, messages.ERROR, e)


# Competition signals
    

