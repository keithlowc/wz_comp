from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.http import FileResponse

from .models import StaffCustomTeams, StaffCustomCompetition, CompetitionCommunicationEmails, ConfigController, PastTournaments, PastTeams
from .forms import JoinCompetitionRequestForm, EmailCommunicationForm, PlayerVerificationForm, CompetitionPasswordRequestForm

from . import signals, util, bg_tasks
from .warzone_api import WarzoneApi

from warzone_general import settings

import requests, datetime, time, ast, json

# Create your views here.

def home(request):
    return render(request, 'main/home.html')

# Competition related
 
def join_request_competition(request, comp_name):
    '''
    This form is used to validate
    users and allow them to sign up
    to the competition.
    '''

    config = ConfigController.objects.get(name = 'main_config_controller')
    competition = StaffCustomCompetition.objects.get(competition_name = comp_name)

    if competition.competition_is_closed:
        context = {
            'competition': competition,
        }
        return render(request, 'competitions/competition_sign_up_is_closed.html', context)

    if request.method == 'POST':

        form = JoinCompetitionRequestForm(request.POST)

        if form.is_valid():
            team = form.save(commit = False)
            team.competition = competition
            team.save()

            # Check if this team will make the competition full
            if competition.teams.all().count() == competition.total_teams_allowed_to_compete:
                competition.competition_is_closed = True
                competition.save()

            signals.send_message.send(sender = None,
                                      request = request,
                                      message = 'Succesfully requested entry to tournament: {}'.format(comp_name),
                                      type = 'SUCCESS')

            return redirect('get_competition', comp_name = comp_name)
    else:
        form = JoinCompetitionRequestForm()
        
        context = {
            'form': form,
            'comp_name': comp_name,
            'config': config,
            'competition': competition
        }

        return render(request, 'forms/join_competition_form.html', context)


def competition_password_request(request, comp_name):
    '''
    This view renders competition password 
    request form. If the competition is set to 
    paid then it will route the user to this view.
    Do not save any data to abstract form.
    '''

    config = ConfigController.objects.get(name = 'main_config_controller')
    competition = StaffCustomCompetition.objects.get(competition_name = comp_name)

    competition_password = competition.competition_password

    if competition.competition_is_closed:

        context = {
            'competition': competition,
        }

        return render(request, 'competitions/competition_sign_up_is_closed.html', context)

    if request.method == 'POST':
        form = CompetitionPasswordRequestForm(request.POST)

        if form.is_valid():
            # We do not save anything 
            # As this is an abstract form
            entry_form = form.save(commit = False)
            
            # Check if password is valid
            if (competition_password == entry_form.password):
                signals.send_message.send(sender = None,
                            request = request,
                            message = 'You have succesfully provided the correct password!',
                            type = 'SUCCESS')

                return redirect('join_request_competition', comp_name = comp_name)

            else:
                signals.send_message.send(sender = None,
                            request = request,
                            message = 'The password you submitted is wrong! Please try again!',
                            type = 'ERROR')

                return redirect('competition_password_request', comp_name = comp_name)
    else:
        form = CompetitionPasswordRequestForm()

        context = {
            'form': form,
            'comp_name': comp_name,
            'competition': competition,
        }

        return render(request, 'forms/competition_password_request.html', context)


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

        bg_tasks.calculate_status_of_competition(custom_config, comp_name, 
                                            repeat = config.competitions_bg_tasks,
                                            repeat_until = competition.end_time + datetime.timedelta(seconds = 120))
        
        if custom_config['competitions_dummy_data']:
            signals.send_message.send(sender = None,
                    request = request,
                    message = 'The data being loaded is Dummy Data! For real data message Admin to change settings',
                    type = 'WARNING')

    return redirect('get_competition', comp_name = comp_name)


def manually_recalculate_score_once(request, comp_name):
    '''
    Allows recalculation of the data
    manually once per click. Background
    job does not keep running.
    '''

    signals.send_message.send(sender = None,
                    request = request,
                    message = 'Manually refreshing once! wait for the status bar to complete! Do not refresh!',
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

        bg_verbose_name = 'manually-calculate-once' + comp_name

        bg_tasks.calculate_status_of_competition_once(verbose_name = bg_verbose_name, 
                                                    custom_config = custom_config, 
                                                    comp_name = comp_name)

        if custom_config['competitions_dummy_data']:
            signals.send_message.send(sender = None,
                    request = request,
                    message = 'The data being loaded is Dummy Data! For real data message Admin to change settings',
                    type = 'WARNING')
        
        # Job starts flag
        competition.manually_calculate_bg_job_status = 'Started'
        competition.save()

    return redirect('get_competition', comp_name = comp_name)


def get_competitions_all(request):
    '''
    Gets all competitions.
    '''

    competitions = StaffCustomCompetition.objects.all().order_by('-start_time')
    config = ConfigController.objects.get(name = 'main_config_controller')

    context = {
        'competitions': competitions,
        'config': config,
    }

    return render(request, 'competitions/competition_main.html', context)


def get_competition(request, comp_name):
    '''
    Gets specific competition
    '''

    config = ConfigController.objects.get(name = 'main_config_controller')
    competition = StaffCustomCompetition.objects.get(competition_name = comp_name)
    teams = StaffCustomTeams.objects.filter(competition = competition.id).order_by('-score', '-checked_in')
    
    context = { 
        'teams': teams,
        'competition': competition,
        'config': config,
    }

    return render(request, 'competitions/competition_scores.html', context)


def get_past_tournaments(request):
    '''
    Gets the past tournament
    results and tables.
    '''

    past_tournaments = PastTournaments.objects.all().order_by('-date_ended')

    context = {
        'past_tournaments': past_tournaments,
    }

    return render(request, 'competitions/past/past_tournaments.html', context)


def migrate_competition_to_past_tournaments(request, comp_name):
    '''
    This view starts a job that migrates the
    data into the PastTournaments model and display it as a
    table format. This will save a lot of rows in the db. 
    '''

    competition = StaffCustomCompetition.objects.get(competition_name = comp_name)
    all_teams = competition.teams.all()
    total_teams = competition.teams.all().count()

    past_tournament_exists = True

    try:
        competition = PastTournaments.objects.get(name = competition.competition_name)
    except Exception as e:
        past_tournament_exists = False
    
    if past_tournament_exists == False:

        past_tournament = PastTournaments.objects.create(name = competition.competition_name, 
                                                        host =  competition.created_by.username,
                                                        date_ended = competition.end_time,
                                                        logo = competition.competition_banner,
                                                        total_teams = total_teams)
    
        for team in all_teams:
            PastTeams.objects.create(tournament = past_tournament, 
                                    name = team.team_name,
                                    email = team.team_captain_email,
                                    data = team.data_to_render,
                                    points = team.score)
        
        # Delete the tournament and redirect
        competition.delete()

        signals.send_message.send(sender = None,
                    request = request,
                    message = 'The tournament has been succesfully migrated to past tournaments!',
                    type = 'SUCCESS')
    
    return redirect('get_past_tournaments')


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

    if len(data_stats) > 0:

        for val in data_stats:
            try:
                for key in val[user]:
                    size = len(val[user])
                    data.append(key[user_key])
            except Exception as e:
                print(e)

        matches = [i for i in range(1, size)]

        average_data = sum(data) / len(data)
        avg = [average_data for i in range(1, size)]
    
    else:
        matches = 0
        data = 0
        avg = 0

    return JsonResponse(data = {
        'matches': matches,
        'key': data,
        'avg': avg,
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


# Competition statistic dashboard

def show_competition_dashboard(request, comp_name):
    context = {
        'comp_name': comp_name,
    }
    return render(request, 'competitions/dashboard/dashboard.html', context)


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


# Verify player

def verify_individual_player(request):
    '''
    Displays form to verify individual player
    and should not be submitted.
    '''

    config = ConfigController.objects.get(name = 'main_config_controller')

    form = PlayerVerificationForm()
    context = {
        'form': form,
        'config': config,
    }
    return render(request, 'verify/public_or_not.html', context)