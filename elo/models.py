from django.db import models
from django.db.models.fields import return_None


class Player(models.Model):
    ign = models.CharField(max_length=16, unique=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ign

class PlayerElo(models.Model):
    player = models.ForeignKey(Player, related_name="elos", on_delete=models.CASCADE)
    gamemode = models.CharField(max_length=100)
    elo = models.IntegerField(default=1000)  
    cat = models.CharField(max_length=10, default="no")  
    last_updated = models.DateTimeField(auto_now=True)


    class Meta:
        unique_together = ('player', 'gamemode')

    @property
    def rank(self):
        if self.elo < 0:
            return "has a j*b"
        elif self.elo < 100:
            return "a cute but dumb cat"
        elif self.elo < 200:
            return "Tier 09 - Combat Apprentice III"
        elif self.elo < 400:
            return "Tier 08-  Combat Apprentice II"
        elif self.elo < 600:
            return "Tier 07 - Combat Apprentice I"
        elif self.elo < 800:
            return "Tier 06 - Combat Adept III"
        elif self.elo < 1000:
            return "Tier 05 - Combat Adept II"
        elif self.elo < 1400:
            return "Tier 04 - Combat Adept I"
        elif self.elo < 1800:
            return "Tier 03 - Elite II"
        elif self.elo < 2200:
            return "Tier 02 - Elite I"
        elif self.elo < 2400:
            return "Tier 01 - Contender"
        else:
            return "get a life"
