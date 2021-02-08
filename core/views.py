from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db import transaction

from .models import StaffCustomTeams, StaffCustomCompetition, CompetitionCommunicationEmails, ConfigController
from .forms import JoinCompetitionRequestForm, EmailCommunicationForm

from . import signals, util, bg_tasks
from .warzone_api import WarzoneApi

from warzone_general import settings

import requests, datetime, time, ast

# Create your views here.

def home(request):
    return render(request, 'main/home.html')

# Competition related
 
def join_request_competition(request, comp_name):
    '''
    Allows you to create
    a team
    '''

    config = ConfigController.objects.get(name = 'main_config_controller')
    competition = StaffCustomCompetition.objects.get(competition_name = comp_name)

    if request.method == 'POST':
        form = JoinCompetitionRequestForm(request.POST)
        if form.is_valid():
            team = form.save(commit = False)
            team.competition = competition
            team.save()

            signals.send_message.send(sender = None,
                                      request = request,
                                      message = 'Succesfully requested entry to tournament: {}'.format(comp_name),
                                      type = 'SUCCESS')

            return redirect('get_competition', comp_name = comp_name)
    else:
        form = JoinCompetitionRequestForm()
    return render(request, 'forms/join_competition_form.html', {'form': form, 'comp_name': comp_name, 'config': config, 'competition': competition})


def recalculate_scores(request, comp_name):
    signals.send_message.send(sender = None,
                    request = request,
                    message = 'Started calculation on the background! Just wait for a couple of minutes and refresh!',
                    type = 'INFO')

    config = ConfigController.objects.get(name = 'main_config_controller')

    custom_config = {
        'cod_x_rapidapi_key': config.cod_x_rapidapi_key,
        'cod_x_rapidapi_host': config.cod_x_rapidapi_host,
        'competitions_dummy_data': config.competitions_dummy_data
    }

    competition = StaffCustomCompetition.objects.get(competition_name = comp_name)

    if competition.competition_started:
        # If competition is ready
        # we set it to false
        competition.competition_started = False
        competition.save()
    else:
        # If competition is not ready = false
        # we set it to True
        competition.competition_started = True
        competition.save()

    if competition.competition_started:
        # if competition is true
        # We activate the bg task

        bg_tasks.calculate_status_of_competition(custom_config, comp_name, repeat = config.competitions_bg_tasks,
                                                 repeat_until = competition.end_time + datetime.timedelta(seconds = 120))
        
        if custom_config['competitions_dummy_data']:
            signals.send_message.send(sender = None,
                    request = request,
                    message = 'The data being loaded is Dummy Data! For real data message Admin to change settings',
                    type = 'WARNING')

    # When press ready
    # if competition ready:
    # the competition will be checking for the time of the comp
    # and start calculating based on that

    return redirect('get_competition', comp_name = comp_name)


def manually_recalculate_score_once(request, comp_name):
    '''
    Allows recalculation of the data
    manually once per click. Background
    job does not keep running.
    '''

    signals.send_message.send(sender = None,
                    request = request,
                    message = 'Manually refreshing once! Make sure to refresh the page!',
                    type = 'INFO')

    config = ConfigController.objects.get(name = 'main_config_controller')

    custom_config = {
        'cod_x_rapidapi_key': config.cod_x_rapidapi_key,
        'cod_x_rapidapi_host': config.cod_x_rapidapi_host,
        'competitions_dummy_data': config.competitions_dummy_data
    }

    competition = StaffCustomCompetition.objects.get(competition_name = comp_name)

    if competition.competition_started:
        # if competition is true
        # We activate the bg task

        print('Manually calling recalculation once!')

        bg_tasks.calculate_status_of_competition(custom_config, comp_name)

        if custom_config['competitions_dummy_data']:
            signals.send_message.send(sender = None,
                    request = request,
                    message = 'The data being loaded is Dummy Data! For real data message Admin to change settings',
                    type = 'WARNING')

    return redirect('get_competition', comp_name = comp_name)


def get_competitions_all(request):
    '''
    Gets all competitions.
    '''

    competitions = StaffCustomCompetition.objects.all()

    context = {
        'competitions': competitions
    }

    return render(request, 'competitions/competition_main.html', context)


def get_competition(request, comp_name):
    '''
    Gets specific competition
    '''

    config = ConfigController.objects.get(name = 'main_config_controller')
    competition = StaffCustomCompetition.objects.get(competition_name = comp_name)
    teams = StaffCustomTeams.objects.filter(competition = competition.id, checked_in = True).order_by('-score')
    
    context = { 
        'teams': teams,
        'competition': competition,
        'config': config,
    }

    return render(request, 'competitions/competition_scores.html', context)

# Charts data

def chart_stats_key(request, team_name, user, key):
    '''
    Provides data depending on the key
    if key = damageDone it will return
    the last values of damagedone based
    on the last few matches before the competition
    '''

    user = user
    user_key = key

    team = StaffCustomTeams.objects.get(team_name = team_name)
    data_stats = team.data_stats

    size = 0
    data = []

    for val in data_stats:
        try:
            for key in val[user]:
                size = len(val[user])
                data.append(key[user_key])
        except Exception as e:
            print(e)

    matches = [i for i in range(1, size)]

    return JsonResponse(data = {
        'matches': matches,
        'key': data,
    })


def show_chart(request):
    return render(request,  'competitions/competition_user_chart.html')


# Competition check in

def check_in_to_competition(request, comp_name, checked_in_uuid):
    '''
    Allows the user to manually
    check in to the tournament
    and edit their teammembers
    or streamer before joining 
    the competition
    '''

    team = get_object_or_404(StaffCustomTeams, checked_in_uuid = checked_in_uuid)

    context = {
        'team': team,
        'uuid': checked_in_uuid,
        'comp_name': comp_name,
    }

    return render(request, 'check_in/check_in.html', context)


def check_in(request, comp_name, team_name, checked_in_uuid):
    '''
    Completes the team check in
    finds the team based on team
    name and uuid and changes
    attribute of checked in to
    True
    '''

    team = StaffCustomTeams.objects.get(team_name = team_name, checked_in_uuid = checked_in_uuid)
    team.checked_in = True
    team.save()

    return redirect('get_competition', comp_name = comp_name)

# Competition Communication

def send_competition_email(request, comp_name):
    '''
    Allows the tournament host to send
    emails to the teams in signed up for the
    competition
    '''
    
    config = ConfigController.objects.get(name = 'main_config_controller')
    competition = StaffCustomCompetition.objects.get(competition_name = comp_name)
    teams = StaffCustomTeams.objects.filter(competition = competition.id)

    sent_emails = CompetitionCommunicationEmails.objects.filter(competition = competition.id).order_by('-date')

    team_emails = [team.team_captain_email for team in teams]

    if request.method == 'POST':
        form = EmailCommunicationForm(request.POST)
        if form.is_valid():
            email = form.save(commit = False)
            email.competition = competition
            email.created_by = request.user
            email.save()

            # Send email
            if config.competition_email_active:
                if len(team_emails) > 0:
                    email_sys = bg_tasks.EmailNotificationSystemJob()
                    email_sys.send_email_update(competition.competition_name, 
                                                email.subject, 
                                                email.body,
                                                team_emails)
                    
                    signals.send_message.send(sender = None,
                                    request = request,
                                    message = 'Succesfully sent email! for competition: {}'.format(comp_name),
                                    type = 'SUCCESS')
                else:
                    signals.send_message.send(sender = None,
                                    request = request,
                                    message = 'Emails will not be sent out since there are no recipients or teams in the competition!',
                                    type = 'WARNING')
            else:
                signals.send_message.send(sender = None,
                                            request = request,
                                            message = 'Email systems are disabled for the current time, this EMAIL will not be sent! - Contact Admin if urgent!',
                                            type = 'WARNING')

            return redirect('send_competition_email', comp_name = comp_name)
    else:
        form = EmailCommunicationForm()
    return render(request, 'forms/email_communication_form.html', {'form': form, 
                                                                'comp_name': comp_name, 
                                                                'team_emails': team_emails, 
                                                                'sent_emails': sent_emails})