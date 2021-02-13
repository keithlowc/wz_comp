from django.shortcuts import render
from django.http import JsonResponse

from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .serializers import MatchSerializer
from core.models import Match


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