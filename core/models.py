from django.db import models
from django.conf import settings

from datetime import datetime

# Create your models here.

class Profile(models.Model):
    activision_tag = models.CharField(max_length = 100, unique = True, null = True)
    account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, null = True)
    kda = models.FloatField(default = 0)
    wins = models.IntegerField(default = 0)
    total_kills = models.IntegerField(default = 0)

    last_ten_matches = models.JSONField(default = dict, blank = True)

    last_calculated_matches = models.JSONField(default = dict, blank = True)

    avg_kills_over_last_ten_matches = models.FloatField(default = 0)
    avg_kda_over_last_ten_matches = models.FloatField(default = 0)
    avg_damage_over_last_ten_matches = models.FloatField(default = 0)

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
    
    def __str__(self):
        return f'{self.activision_tag}'

class Teams(models.Model):
    team_types = [
        ('SQUAD', 'squad'),
        ('TRIOS', 'trios'),
        ('DUOS', 'duos'),
        ('SOLOS', 'solos')
    ]
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, default = 0)
    profiles = models.ManyToManyField(Profile)
    team_name = models.CharField(max_length = 100, null = True, unique = True)
    team_type = models.CharField(
        max_length = 5,
        choices = team_types,
        default = 'SQUAD'
    )
    cummulative_kd = models.FloatField(default = 0)
    total_wins = models.IntegerField(default = 0)
    total_kills = models.IntegerField(default = 0)

    class Meta:
        verbose_name = 'Teams'
        verbose_name_plural = 'Teams'
    
    def __str__(self):
        return str(self.team_name) + ' - ' + str(self.team_type)

# Custom competitions
class StaffCustomCompetition(models.Model):
    competition_name = models.CharField(max_length = 150, null = True, unique = True)
    competition_description = models.CharField(max_length = 500, null = True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, default = 0)
    
    # Rules
    points_per_kill = models.IntegerField(default = 1)
    points_per_first_place = models.IntegerField(default = 1)
    points_per_second_place = models.IntegerField(default = 1)
    points_per_third_place = models.IntegerField(default = 1)

    start_time = models.DateTimeField(default = datetime.now, blank = True)
    end_time = models.DateTimeField(default = datetime.now, blank = True)

    # Competition flag should flip based on time started
    competition_ready = models.BooleanField(default = False)

    # Status
    # 'In-Progress': 1,
    # 'Ended': 2,
    # 'Not started': 3,

    competition_status = models.IntegerField(default = 3)

    # timezones = [
    #     ('EST', 'est'),
    #     ('UTC', 'utc'),
    # ]

    # competition_timezone = models.CharField(
    #     max_length = 5,
    #     choices = timezones,
    #     default = 'EST'
    # )

    class Meta:
        verbose_name = 'CustomCompetition'
        verbose_name_plural = 'CustomCompetitions'
    
    def __str__(self):
        return str(self.competition_name)


class StaffCustomTeams(models.Model):
    player_1 = models.CharField(max_length = 100, null = True, unique = True, blank = True)
    player_2 = models.CharField(max_length = 100, null = True, unique = True, blank = True)
    player_3 = models.CharField(max_length = 100, null = True, unique = True, blank = True)
    player_4 = models.CharField(max_length = 100, null = True, unique = True, blank = True)

    competition = models.ForeignKey(StaffCustomCompetition, on_delete = models.CASCADE)

    data = models.JSONField(default = dict, blank = True)
    data_to_score = models.JSONField(default = dict, blank = True)

    score = models.IntegerField(default = 0)
    
    team_name = models.CharField(max_length = 100, null = True, unique = True)

    class Meta:
        verbose_name = 'CustomTeam'
        verbose_name_plural = 'CustomTeams'
    
    def __str__(self):
        return str(self.team_name)


class ConfigController(models.Model):
    '''
    Based on this config controller
    we can control the time
    to run background jobs, refresh and 
    etc
    
    For development:

    competitions_page_refresh_time = 5000 mili seconds
    competitions_bg_tasks = 100 seconds
    '''
    competitions_page_refresh_time = models.IntegerField(default = 5000)
    competitions_bg_tasks = models.IntegerField(default = 100)

    class Meta:
        verbose_name = 'ConfigController'
        verbose_name_plural = 'ConfigControllers'
    
    def __str__(self):
        return str("Configuration controller - Do not delete - Do not create more objects")

