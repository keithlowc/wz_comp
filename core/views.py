from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, FileResponse
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from .models import StaffCustomTeams, StaffCustomCompetition, CompetitionCommunicationEmails, ConfigController, PastTournaments, PastTeams, Profile, Regiment
from .forms import JoinCompetitionRequestForm, EmailCommunicationForm, PlayerVerificationForm, CompetitionPasswordRequestForm, RocketLeagueForm, ProfileForm, RegimentForm

from silk.profiling.profiler import silk_profile
from . import signals, util, bg_tasks
from .warzone_api import WarzoneApi

import requests, datetime, time, ast, json

# Create your views here.

def home(request):
    return render(request, 'main/home.html')

def get_privacy_policy(request):
    return render(request, 'main/privacy_policy.html')

# User profile patch

@login_required
def get_or_create_profile(request):
    '''
    Returns the profile of the user
    and allows them to edit it
    '''
    config = ConfigController.objects.get(name = 'main_config_controller')

    custom_config = {
        'cod_x_rapidapi_key': config.cod_x_rapidapi_key,
        'cod_x_rapidapi_host': config.cod_x_rapidapi_host,
        'competitions_dummy_data': config.competitions_dummy_data,
        'anomaly_detection_active': config.anomaly_detection_active,
    }

    try:
        profile = Profile.objects.get(user = request.user)
    except Profile.DoesNotExist as e:
        print('Does not exist')
        profile = None
    
    # Find all the teams he is part of
    regiments = Regiment.objects.filter(members = profile)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance = profile)

        if form.is_valid():
            print('Form is valid!')
            profile_form = form.save(commit = False)
            profile_form.user = request.user
            profile_form.save()

            bg_tasks.verify_user_profile_warzone_tag(custom_config = custom_config,
                                                    user = request.user.id, 
                                                    wz_tag = profile_form.warzone_tag, 
                                                    wz_tag_type = profile_form.warzone_tag_type)

            signals.send_message.send(sender = None,
                                    request = request,
                                    message = 'You have succesfully updated your profile',
                                    type = 'SUCCESS')

            return redirect('get_or_create_profile')

    form = ProfileForm(instance = profile)
    
    context = {
        'form': form,
        'regiments': regiments,
        'profile': profile,
    }

    return render(request, 'user_profiles/profile.html', context = context)

@login_required
def get_regiment_profile(request, regiment_name):
    '''
    Returns the team profile page
    '''

    # try:

    regiment = Regiment.objects.get(name = regiment_name)

    context = {
        'name': regiment.name,
        'members': regiment.members.all(),
        'description': regiment.description,
        'invite_code': regiment.invite_code,
        'leader': regiment.leader,
    }

    return render(request, 'regiments/regiment.html', context = context)
    # except Exception as e:
    #     context = {}
    #     return render(request, 'regiments/regiment.html', context = context)

@login_required
def regiment_join_confirmation(request, regiment_name, invite_code):
    '''
    Shows a form for the user to 
    confirm regiment join
    '''

    regiment_exists = False
    user_is_part_of_regiment = False

    # You are already part of the regiment

    try:
        regiment = Regiment.objects.get(name = regiment_name, invite_code = invite_code)
        regiment_exists = True
    except Exception as e:
        print(e)
        regiment_exists = False
    
    if regiment_exists:
        try:
            regiment.members.all().get(user = request.user)
            user_is_part_of_regiment = True
        except Exception:
            user_is_part_of_regiment = False

    context = {
        'regiment_name': regiment_name,
        'regiment_exist': regiment_exists,
        'invite_code': invite_code,
        'user_is_part_of_regiment': user_is_part_of_regiment,
    }

    return render(request, 'regiments/regiment_join_confirmation.html', context = context)

@login_required
def join_regiment(request, regiment_name, invite_code):
    '''
    Allows the user to join the team
    with the given invitation code
    '''
    
    try:
        regiment = Regiment.objects.get(name = regiment_name, invite_code = invite_code)
        profile = Profile.objects.get(user = request.user)
        regiment.members.add(profile)
        regiment.save()

        signals.send_message.send(sender = None,
                request = request,
                message = 'You have joined the team',
                type = 'SUCCESS')

    except Exception as e:
        signals.send_message.send(sender = None,
            request = request,
            message = 'There was an issue joining the team with error {}'.format(e),
            type = 'WARNING')

    return redirect('get_regiment_profile', regiment_name = regiment_name)

@login_required
def create_regiment(request):
    '''
    Create regiment view and form
    '''
    profile = Profile.objects.get(user = request.user)
    regiment_count = Regiment.objects.filter(members = profile).count()

    if request.method == 'POST':
        form = RegimentForm(request.POST)
        
        if regiment_count < 5:

            if form.is_valid():
                
                regiment_form = form.save(commit = False)
                regiment_form.leader = profile
                regiment_form.save()
                regiment_form.members.set([profile])

                signals.send_message.send(sender = None,
                    request = request,
                    message = 'Successfully created regiment',
                    type = 'SUCCESS')
                
                return redirect('get_or_create_profile')
        else:
            signals.send_message.send(sender = None,
                request = request,
                message = 'Cannot be part of more than 5 regiments - Please leave at least one regiment.',
                type = 'WARNING')

            return redirect('get_or_create_profile')
            
    form = RegimentForm()

    context = {
        'form': form,
        'regiment_editing': False,
    }

    return render(request, 'regiments/forms/regiment_creation.html', context = context)

@login_required
def edit_regiment(request, regiment_name):
    '''
    Edit regiment view
    '''

    profile = Profile.objects.get(user = request.user)
    regiment_instance = Regiment.objects.get(leader = profile, name = regiment_name)

    new_regiment_name = ''

    if request.method == 'POST':
        form = RegimentForm(request.POST, instance = regiment_instance)
        if form.is_valid():
            regiment_form = form.save(commit = False)
            new_regiment_name = regiment_form.name
            form.save()

            signals.send_message.send(sender = None,
                    request = request,
                    message = 'Successfully edited regiment',
                    type = 'SUCCESS')
            
            return redirect('get_regiment_profile', regiment_name = new_regiment_name)

    form = RegimentForm(instance = regiment_instance)

    context = {
        'form': form,
        'regiment_editing': True,
    }

    return render(request, 'regiments/forms/regiment_creation.html', context = context)

@login_required
def leave_regiment(request, regiment_name):
    '''
    Leave regiment
    '''
    profile = Profile.objects.get(user = request.user)
    regiment = Regiment.objects.get(name = regiment_name)

    total_members = regiment.members.all().count()

    if total_members > 1:

        if regiment.leader == profile:
            regiment.members.remove(profile)
            regiment_members = regiment.members
            regiment.leader = regiment.members.all()[0]
            regiment.save()

            signals.send_message.send(sender = None,
                request = request,
                message = 'Successfully left the regiment',
                type = 'SUCCESS')

            return redirect('get_or_create_profile')
        
        else:
            regiment.members.remove(profile)
            regiment.save()

            signals.send_message.send(sender = None,
                request = request,
                message = 'Successfully left the regiment',
                type = 'SUCCESS')

            return redirect('get_or_create_profile')
    
    else:
        regiment.delete()
        signals.send_message.send(sender = None,
            request = request,
            message = 'Successfully left the regiment and deleted it',
            type = 'SUCCESS')
        
        return redirect('get_or_create_profile')

@login_required
def remove_member_from_regiment(request, regiment_name, member_username):
    '''
    Remove the member from the regiment
    '''

    User = get_user_model()

    user_to_remove = User.objects.get(username = member_username)
    member_to_remove_profile = Profile.objects.get(user = user_to_remove)
    regiment = Regiment.objects.get(name = regiment_name)
    regiment.members.remove(member_to_remove_profile)

    signals.send_message.send(sender = None,
        request = request,
        message = 'Successfully removed member from regiment',
        type = 'WARNING')

    return redirect('get_regiment_profile', regiment_name = regiment_name)




# Data remediation
def remediate_kds(request, comp_name):
    '''
    Manually loads all players
    kd's
    '''

    competition = StaffCustomCompetition.objects.get(competition_name = comp_name)

    config = ConfigController.objects.get(name = 'main_config_controller')

    custom_config = {
        'cod_x_rapidapi_key': config.cod_x_rapidapi_key,
        'cod_x_rapidapi_host': config.cod_x_rapidapi_host,
        'competitions_dummy_data': config.competitions_dummy_data,
        'anomaly_detection_active': config.anomaly_detection_active,
    }
    
    bg_tasks.remediate_users_kd(custom_config = custom_config, comp_name = comp_name)

    signals.send_message.send(sender = None,
                request = request,
                message = 'Remediating data',
                type = 'INFO')
    
    # Job starts flag
    competition.manually_calculate_bg_job_status = 'Started'
    competition.save()

    return redirect('get_competition', comp_name = comp_name)

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
    
    signals.send_message.send(sender = None,
                            request = request,
                            message = 'Something went wrong..',
                            type = 'DANGER')
    
    return redirect('get_competition', comp_name = comp_name)


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


@silk_profile(name='Recalculate scores')
def recalculate_scores(request, comp_name):
    signals.send_message.send(sender = None,
                    request = request,
                    message = 'Started calculation on the background! Just wait for a couple of minutes and refresh!',
                    type = 'INFO')

    config = ConfigController.objects.get(name = 'main_config_controller')

    custom_config = {
        'cod_x_rapidapi_key': config.cod_x_rapidapi_key,
        'cod_x_rapidapi_host': config.cod_x_rapidapi_host,
        'competitions_dummy_data': config.competitions_dummy_data,
        'anomaly_detection_active': config.anomaly_detection_active,
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
        
        # Job starts flag
        competition.manually_calculate_bg_job_status = 'Scheduled'
        competition.save()

    return redirect('get_competition', comp_name = comp_name)


@silk_profile(name='Manually recalculate once')
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
        'competitions_dummy_data': config.competitions_dummy_data,
        'anomaly_detection_active': config.anomaly_detection_active,
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


@silk_profile(name='Get all competitions')
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


@silk_profile(name='Get competition')
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
                                    email_captain = team.team_captain_email,
                                    player_1 = team.player_1,
                                    player_1_id_type = team.player_1_id_type,

                                    player_2_email = team.player_2_email,
                                    player_2 = team.player_2,
                                    player_2_id_type = team.player_2_id_type,

                                    player_3_email = team.player_3_email,
                                    player_3 = team.player_3,
                                    player_3_id_type = team.player_3_id_type,

                                    player_4_email = team.player_4_email,
                                    player_4 = team.player_4,
                                    player_4_id_type = team.player_4_id_type,

                                    points = team.score)
        
        # Delete the tournament and redirect
        competition.delete()

        signals.send_message.send(sender = None,
                    request = request,
                    message = 'The tournament has been succesfully migrated to past tournaments!',
                    type = 'SUCCESS')
    
    return redirect('get_past_tournaments')


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

    signals.send_message.send(sender = None,
                            request = request,
                            message = 'You have succesfully checked in your team: {}'.format(team_name),
                            type = 'SUCCESS')

    return redirect('get_competition', comp_name = comp_name)


# Competition statistic dashboard

def show_competition_dashboard(request, comp_name):
    context = {
        'comp_name': comp_name,
    }
    return render(request, 'competitions/dashboard/dashboard.html', context)


def show_chart(request):
    return render(request,  'competitions/competition_user_chart.html')


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


# Temporary Rocket League

def show_rocket_league_form(request):

    if request.method == 'POST':
        form = RocketLeagueForm(request.POST)
        if form.is_valid():
            rocket = form.save(commit = False)
            team_name = rocket.team_name
            rocket.save()

            signals.send_message.send(sender = None,
                                    request = request,
                                    message = 'Your team {} has succesfully been entered to Total Upgrade competition'.format(team_name),
                                    type = 'SUCCESS')

            return redirect('show_rocket_league_form')

    form = RocketLeagueForm()

    context = {
        'form': form,
    }
    return render(request, 'forms/rocket_league_form.html', context)