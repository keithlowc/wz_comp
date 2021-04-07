from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from .serializers import MatchSerializer
from core.models import Player, Match, StaffCustomCompetition


@api_view(['GET'])
def api_matches_overview(request):
    '''
    Provides overview of what
    the user can do with the rest
    api
    '''

    api_urls = {
        '[GET] get_all_matches': '/api/match/all',
        '[GET] get_matches_with_id': 'api/match/<int:match_id>/',
        '[GET] get_top_killers': 'api/match/stats/topkillers/<str:comp_name>',
        '[GET] get_top_headshots': 'api/match/stats/topheadshots/<str:comp_name>',
        '[GET] get_top_deaths': 'api/match/stats/topdeaths/<str:comp_name>',
        '[GET] get_top_damage_by_team': 'api/match/stats/topdamageperteam/<str:comp_name>',
        '[GET] get_top_damage_taken_by_team': 'api/match/stats/topdamagetakenperteam/<str:comp_name>',
    }

    return Response(api_urls)


@api_view(['GET'])
def get_all_matches(request):
    '''
    Gets all the matches in
    '''

    matches = Match.objects.all()
    serialized_matches = MatchSerializer(matches, many = True)
    return Response(serialized_matches.data)


@api_view(['GET'])
def get_matches_with_id(request, match_id):
    '''
    Gets all matches with the id 
    priovided
    '''

    matches = Match.objects.filter(match_id = match_id)
    serialized_matches = MatchSerializer(matches, many = True)
    return Response(serialized_matches.data)


@api_view(['GET'])
def get_top_killers(request, comp_name):
    '''
    Competition STATS:

    Get the top killers of the competition
    '''

    competition = get_object_or_404(StaffCustomCompetition, competition_name = comp_name)

    players = Player.objects.filter(competition = competition)

    players_dict = {}
    for index, player in enumerate(players):
        matches = Match.objects.filter(player = player)

        kill = []
        for match in matches:
            kill.append(match.kills)
        
        players_dict[player.user_id] = sum(kill)

    return Response(players_dict)


@api_view(['GET'])
def get_top_headshots(request, comp_name):
    '''
    Competition STATS:

    Get the top headshots of the competition
    '''

    competition = get_object_or_404(StaffCustomCompetition, competition_name = comp_name)

    players = Player.objects.filter(competition = competition)

    players_dict = {}
    for index, player in enumerate(players):
        matches = Match.objects.filter(player = player)

        kill = []
        for match in matches:
            kill.append(match.headshots)
        
        players_dict[player.user_id] = sum(kill)

    return Response(players_dict)


@api_view(['GET'])
def get_top_deaths(request, comp_name):
    '''
    Competition STATS:

    Get the top deaths of the competition
    '''

    competition = get_object_or_404(StaffCustomCompetition, competition_name = comp_name)

    players = Player.objects.filter(competition = competition)

    players_dict = {}
    for index, player in enumerate(players):
        matches = Match.objects.filter(player = player)

        kill = []
        for match in matches:
            kill.append(match.deaths)
        
        players_dict[player.user_id] = sum(kill)

    return Response(players_dict)


@api_view(['GET'])
def get_top_damage_by_team(request, comp_name):
    '''
    Competition STATS:

    Get the top damage made by team
    '''

    competition = get_object_or_404(StaffCustomCompetition, competition_name = comp_name)

    teams = competition.teams.all()

    damage_per_team = {}

    for team in teams:
        damage_list = []
        matches_per_team = Match.objects.filter(competition = competition, team = team)

        for match in matches_per_team:
            damage_list.append(match.damage_done)
        
        damage_per_team[team.team_name] = sum(damage_list)

    return Response(damage_per_team)


@api_view(['GET'])
def get_top_damage_taken_by_team(request, comp_name):
    '''
    Competition STATS:

    Get the top damage made by team
    '''

    competition = get_object_or_404(StaffCustomCompetition, competition_name = comp_name)

    teams = competition.teams.all()

    damage_taken_per_team = {}

    for team in teams:
        damage_taken_list = []
        matches_per_team = Match.objects.filter(competition = competition, team = team)

        for match in matches_per_team:
            damage_taken_list.append(match.damage_taken)
        
        damage_taken_per_team[team.team_name] = sum(damage_taken_list)

    return Response(damage_taken_per_team)


@api_view(['GET'])
def get_type_of_players(request, comp_name):
    '''
    Competition STATS:

    Get the type of players
    '''

    competition = get_object_or_404(StaffCustomCompetition, competition_name = comp_name)

    players = competition.players.all()

    player_type = {
        'battle': 0,
        'psn': 0,
        'xbl': 0,
    }

    for player in players:
        if player.user_id_type == 'battle':
            player_type['battle'] += 1
        elif player.user_id_type == 'psn':
            player_type['psn'] += 1
        elif player.user_id_type == 'xbl':
            player_type['xbl'] += 1

    return Response(player_type)


@api_view(['GET'])
@permission_classes((AllowAny, ))
def get_bg_job_status(request, comp_name):
    '''
    Retrieves the bg job status
    Active or inactive
    '''
    
    competition = get_object_or_404(StaffCustomCompetition, competition_name = comp_name)

    context = {
        'status': competition.manually_calculate_bg_job_status,
    }

    return Response(context)

