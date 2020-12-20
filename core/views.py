from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db import transaction

from .models import Profile, Teams, StaffCustomTeams, StaffCustomCompetition, ConfigController
from .forms import ProfileForm, TeamsForm

from . import signals, util, bg_tasks
from .warzone_api import WarzoneApi

import requests, datetime, time, ast, os

# Create your views here.

def home(request):
    return render(request, 'main/home.html')

@transaction.atomic
def refresh_profile(request):
    '''
    Allows a manual refresh
    of the users account.
    '''

    profile = Profile.objects.filter(account = request.user.id)

    if len(profile) > 0:

        warzone_api = WarzoneApi(tag = profile[0].activision_tag, 
                                platform = 'acti')

        try:
            battle_royale_general_stats = warzone_api.get_warzone_general_stats()
            battle_royale_general_stats = battle_royale_general_stats['br']

        except Exception as e:
            error = battle_royale_general_stats['error']
            signals.send_message.send(sender = None,
                        request = request,
                        message = 'Error from refresh_profile: {}'.format(e),
                        type = 'ERROR')

            if error:
                context = {
                    'profile_found': False,
                    'message': 'I was unable to find your Activision id. Make sure to edit it to the correct number'
                }

                signals.send_message.send(sender = None,
                                          request = request,
                                          message = 'Cannot find your activision id. Make sure you have the correct one and edit it.',
                                          type = 'SUCCESS')

                return render(request, 'profile/profile.html', context)
        
        time.sleep(1)

        try:
            battle_royale_matches = warzone_api.get_warzone_matches()
            last_ten_matches = battle_royale_matches['matches'][0:10]

        except Exception as e:
            
            error = battle_royale_general_stats['error']
            signals.send_message.send(sender = None,
                        request = request,
                        message = 'Error from refresh_profile: {}'.format(e),
                        type = 'ERROR')

            if error:
                context = {
                    'profile_found': False,
                    'message': 'I was unable to find your Activision id. Make sure to edit it to the correct number'
                }

                signals.send_message.send(sender = None,
                                          request = request,
                                          message = 'Cannot find your activision id. Make sure you have the correct one and edit it.',
                                          type = 'SUCCESS')

                return render(request, 'profile/profile.html', context)

        avg_kills_over_last_ten_matches = util.calculate_average(last_ten_matches, 'kills')
        avg_kda_over_last_ten_matches = util.calculate_average(last_ten_matches, 'kdRatio')
        avg_damage_over_last_ten_matches = util.calculate_average(last_ten_matches, 'damageDone')

        profile[0].kda = '{:.2f}'.format(battle_royale_general_stats['kdRatio'])
        profile[0].wins = battle_royale_general_stats['wins']
        profile[0].total_kills = battle_royale_general_stats['kills']

        profile[0].last_ten_matches = last_ten_matches
        profile[0].avg_kills_over_last_ten_matches = avg_kills_over_last_ten_matches
        profile[0].avg_kda_over_last_ten_matches = avg_kda_over_last_ten_matches
        profile[0].avg_damage_over_last_ten_matches = avg_damage_over_last_ten_matches

        profile[0].save()

        signals.send_message.send(sender = None,
                                request =  request,
                                message = 'Refreshed account succesfully!',
                                type =    'SUCCESS')

        return redirect('view_profile')

    else:
        return redirect('view_profile')


def view_profile(request):
    profile = Profile.objects.filter(account = request.user.id)

    if len(profile) > 0:

        activision_tag = profile[0].activision_tag

        last_ten_matches = util.get_values_from_matches(profile[0].last_ten_matches)

        context = {
            'profile_found': True,
            'activision_tag' : activision_tag,
            'battleroyale_total_wins' : profile[0].wins,
            'kdratio' : '{:.2f}'.format(profile[0].kda),
            'total_kills' : profile[0].total_kills,

            'last_ten_matches': last_ten_matches,
            'avg_kills_over_last_ten_matches': profile[0].avg_kills_over_last_ten_matches,
            'avg_kda_over_last_ten_matches': profile[0].avg_kda_over_last_ten_matches,
            'avg_damage_over_last_ten_matches': profile[0].avg_damage_over_last_ten_matches,

            'message' : 'Your account is in good standing!',
        }

        return render(request, 'profile/profile.html', context)

    else:
        return redirect('edit_profile')


def get_profile(request, tag):
    '''
    Gets an users profile
    view mode only.
    '''

    profile = get_object_or_404(Profile, activision_tag = tag)

    activision_tag = profile.activision_tag

    last_ten_matches = util.get_values_from_matches(profile.last_ten_matches)

    context = {
        'profile_found': True,
        'activision_tag' : activision_tag,
        'battleroyale_total_wins' : profile.wins,
        'kdratio' : '{:.2f}'.format(profile.kda),
        'total_kills' : profile.total_kills,

        'last_ten_matches': last_ten_matches,
        'avg_kills_over_last_ten_matches': profile.avg_kills_over_last_ten_matches,
        'avg_kda_over_last_ten_matches': profile.avg_kda_over_last_ten_matches,

        'message' : 'Your account is in good standing!',
    }

    return render(request, 'profile/profile.html', context)


def edit_profile(request):
    '''
    Allows you to edit
    your own profile
    '''

    try:
        my_instance = get_object_or_404(Profile, account = request.user.id)

        if request.method == "POST":

            form = ProfileForm(request.POST, instance = my_instance)
            
            if form.is_valid():
                profile = form.save(commit = False)
                profile.account = request.user
                profile.save()

                signals.send_message.send(sender = None,
                                          request = request,
                                          message = 'Succesfully edited the profile',
                                          type = 'SUCCESS')

                signals.recalculate_stats.send(sender = None,
                                                request = request,
                                                activision_tag = profile)
        
                return redirect('view_profile')

    except Exception as e:
        print('There was an issue {}'.format(e))
        signals.send_message.send(sender = None,
                                    request = request,
                                    message = 'Error from edit_profile: {}'.format(e),
                                    type = 'ERROR')

    if request.method == "POST":

        form = ProfileForm(request.POST)

        if form.is_valid():
            profile = form.save(commit = False)
            profile.account = request.user
            profile.save()

            signals.send_message.send(sender = None,
                                      request = request,
                                      message = 'Succesfully edited the profile',
                                      type = 'SUCCESS')
            
            signals.recalculate_stats.send(sender = None,
                                            request = request,
                                            activision_tag = profile)

            return redirect('view_profile')
    else:
        form = ProfileForm()
    return render(request, 'forms/profile_form.html', {'form': form})


def view_teams(request):
    '''
    Provides a general view
    of the teams created by 
    the logged user or if they
    are part of another team.
    '''
    try:
        profile = get_object_or_404(Profile, account = request.user.id)

        teams = Teams.objects.filter(profiles = profile.id).prefetch_related('profiles')

        context = {
            'teams': teams,
            'user': request.user,
        }

        return render(request, 'teams/your_teams.html', context)
    
    except Exception as e:

        signals.send_message.send(sender = None,
                                request = request,
                                message = 'Error from view_teams: {}'.format(e),
                                type = 'ERROR')

        return render(request, 'main/home.html')


def view_team(request, team_name):
    '''
    View individual team
    with stats
    '''

    team = get_object_or_404(Teams.objects.prefetch_related('profiles'), team_name = team_name)

    profiles = team.profiles.all()

    context = {
        'profiles': profiles,
        'team': team,
        'user': request.user,
    }


    return render(request, 'teams/team.html', context)


def create_team(request):
    '''
    Allows you to create
    a team
    '''

    if request.method == "POST":
        form = TeamsForm(request.POST)
        if form.is_valid():
            teams = form.save(commit = False)
            teams.created_by = request.user
            teams.save()
            form.save_m2m() # Needed when saving many to many fields

            signals.send_message.send(sender = None,
                                      request = request,
                                      message = 'Succesfully edited the teams',
                                      type = 'SUCCESS')

            signals.recalculate_stats_for_team.send(sender = None,
                                                    request = request,
                                                    profiles = teams.profiles.all(),
                                                    team_name = teams.team_name)

            return redirect('view_teams')
    else:
        form = TeamsForm()
    return render(request, 'forms/team_form.html', {'form': form})


def edit_team(request, team_name):
    '''
    Allows to edit the team 
    only if you have created the 
    team
    '''

    instance = get_object_or_404(Teams, created_by = request.user.id, team_name = team_name)

    if request.method == 'POST':
        form = TeamsForm(request.POST, instance = instance)
        if form.is_valid():
            teams = form.save(commit = False)
            teams.save()
            form.save_m2m() # Needed when saving many to many fields

            signals.send_message.send(sender = None,
                                      request = request,
                                      message = 'Succesfully edited the teams',
                                      type = 'SUCCESS')
            
            signals.recalculate_stats_for_team.send(sender = None,
                                                    request = request,
                                                    profiles = teams.profiles.all(),
                                                    team_name = teams.team_name)
            return redirect('view_teams')
    else:
        form = TeamsForm(instance = instance)
        return render(request, 'forms/team_form.html', {'form': form})


@transaction.atomic
def delete_team(request, team_name):
    try:
        Teams.objects.filter(team_name = team_name).delete()
        signals.send_message.send(sender = None,
                                request = request,
                                message = 'Succesfully deleted the team!',
                                type = 'INFO')

        return redirect('view_teams')
    
    except Exception as e:
        signals.send_message.send(sender = None,
                                request = request,
                                message = 'Error from delete_team: {}'.format(e),
                                type = 'ERROR')
        
        return redirect('view_teams')


@transaction.atomic
def leave_team(request, team_name):
    '''
    Removes the relationship
    of an user to a team.
    '''
    try:
        team = Teams.objects.get(team_name = team_name)
        user = Profile.objects.get(account = request.user.id)

        team.profiles.remove(user)
        signals.send_message.send(sender = None,
                                request = request,
                                message = 'You have succesfully left the team',
                                type = 'INFO')
        
        signals.recalculate_stats_for_team.send(sender = None,
                                                request = request,
                                                profiles = team.profiles.all(),
                                                team_name = team_name)

        return redirect(view_teams)
    
    except Exception as e:
        signals.send_message.send(sender = None,
                                request = request,
                                message = 'Error from leave_team: {}'.format(e),
                                type = 'ERROR')

        return redirect(view_teams)


# Competition related

def recalculate_scores(request, comp_name):
    signals.send_message.send(sender = None,
                    request = request,
                    message = 'Started calculation on the background! Just wait for a couple of minutes and refresh!',
                    type = 'INFO')

    config = ConfigController.objects.get(name = 'ConfigController')
    competition = StaffCustomCompetition.objects.get(competition_name = comp_name)

    if competition.competition_ready:
        # If competition is ready
        # we set it to false
        competition.competition_ready = False
        competition.save()
    else:
        # If competition is not ready = false
        # we set it to True
        competition.competition_ready = True
        competition.save()

    if competition.competition_ready:
        # if competition is true
        # We activate the bg task

        bg_tasks.calculate_status_of_competition(comp_name, repeat = config.competitions_bg_tasks, repeat_until = competition.end_time) # 10 minuticos mas

    # When press ready
    # if competition ready:
    # the competition will be checking for the time of the comp
    # and start calculating based on that

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

    try:
        config = ConfigController.objects.get(name = 'main_config_controller')
        competition = StaffCustomCompetition.objects.get(competition_name = comp_name)
        teams = StaffCustomTeams.objects.filter(competition = competition.id).order_by('-score')
    except Exception as e:
        print(e)
    
    context = { 
        'teams': teams,
        'competition': competition,
        'config': config,
    }

    return render(request, 'competitions/competition_scores.html', context)
