from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.parsers import JSONParser

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .serializers import MatchSerializer
from core.models import Match


class AllMatchesViewSet(viewsets.ModelViewSet):
    '''
    Gets all current matches
    '''

    queryset = Match.objects.all()
    serializer_class = MatchSerializer


@csrf_exempt
def get_match(request, match_id):
    if request.method == 'GET':
        match = Match.objects.get(match_id = match_id)
        serialized_match = MatchSerializer(match)
        
        return JsonResponse(serialized_match.data)