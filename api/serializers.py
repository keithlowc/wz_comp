from rest_framework import serializers

from core.models import Match


class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ['competition', 'team', 'match_id', 
                'user_id', 'user_id_type', 'kills',
                'kd', 'damage_done', 'damage_taken',
                'placement']