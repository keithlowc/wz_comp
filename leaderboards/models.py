from django.db import models

# Create your models here.

class Teams(models.Model):
    record_modes = [
        ('Solos','Solos'),
        ('Duos','Duos'),
        ('Trios','Trios'),
        ('Squads','Squads'),
    ]

    team_name = models.CharField(max_length = 15)
    kills = models.IntegerField()
    record_mode = models.CharField(max_length = 6, choices = record_modes)

    class Meta:
        verbose_name = 'Team'
        verbose_name_plural = 'Teams'

    def __str__(self):
        return str(self.team_name)