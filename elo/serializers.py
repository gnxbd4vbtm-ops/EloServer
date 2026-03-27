from rest_framework import serializers
from .models import Player, PlayerElo

class PlayerEloSerializer(serializers.ModelSerializer):
    rank = serializers.ReadOnlyField()  # return the rank property

    class Meta:
        model = PlayerElo
        fields = ['gamemode', 'elo', 'rank', 'last_updated']

class PlayerSerializer(serializers.ModelSerializer):
    elos = PlayerEloSerializer(many=True, read_only=True)

    class Meta:
        model = Player
        fields = ['ign', 'elos', 'last_updated']
