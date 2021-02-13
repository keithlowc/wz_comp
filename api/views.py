from django.shortcuts import render
from django.http import JsonResponse

from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

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

    competition = StaffCustomCompetition.objects.get(competition_name = comp_name)

    players = Player.objects.filter(competition = competition)

    print(players)

    # users = []
    # for team in competition.teams.all():
    #     users.append(team.player_1)
    #     users.append(team.player_2)
    #     users.append(team.player_3)
    #     users.append(team.player_4)
    
    # Pops none values out of list
    # cleaned_user_list = [i for i in users if i]

    player_list = [player.user_id for player in players]

    # Creates the dictionary of users
    users_dict = {}
    for index, user in enumerate(player_list):
        users_dict[user] = index
    
    # Calculates the total kills per player
    for user, kills in users_dict.items():
        user_matches = Match.objects.filter(user_id = user)
        kills = []
        for match in user_matches:
            user_kills_per_match = match.kills
            kills.append(user_kills_per_match)
        
        users_dict[user] = sum(kills)

    return Response(users_dict)