from rest_framework import serializers

from core.models import Match


class MatchSerializer(serializers.ModelSerializer):
    '''
    Serializer for matches
    '''

    class Meta:
        model = Match
        fields = '__all__'