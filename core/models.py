from django.db import models
from django.conf import settings
from django.contrib import admin

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
    competition_type = [
        ('SQUADS', 'SQUADS'),
        ('TRIOS', 'TRIOS'),
        ('DUOS', 'DUOS'),
        ('SOLOS', 'SOLOS'),
    ]

    competition_name = models.CharField(max_length = 150, null = True, unique = True)
    competition_description = models.TextField(default = '')
    competition_type = models.CharField(max_length = 6, choices = competition_type)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, default = 0)
    competition_banner = models.URLField(max_length = 1000, default = 'https://cdn1.dotesports.com/wp-content/uploads/2019/12/16125403/cod38.jpg')
    total_teams_allowed_to_compete = models.IntegerField(default = 30, null = True)

    # Contact Information
    discord_link = models.URLField(max_length = 1000, null = True, blank = True)
    instagram_link = models.URLField(max_length = 1000, null = True, blank = True)
    facebook_link = models.URLField(max_length = 1000, null = True, blank = True)
    twitter_link = models.URLField(max_length = 1000, null = True, blank = True)
    twitch_link = models.URLField(max_length = 1000, null = True, blank = True)
    
    # Verification rules
    cod_kd_maximum_per_player_verification = models.FloatField(default = 3, verbose_name = "Account Verification: KD maximum per player (Default = 3)")
    cod_kd_minimum_per_player_verification = models.FloatField(default = 1, verbose_name = "Account Verification: KD minimum per player (Default = 1)")

    cod_verification_total_games_played = models.IntegerField(default = 100, verbose_name = "Account Verification: Total amount of matches needed to verify account (Default = 100 games)") # 50 games total
    cod_verification_total_time_played = models.IntegerField(default = 5, verbose_name = "Account Verification: Total amount of time played to verify account (Default = 5 days)") # epoch seconds per day - 86400 * 5 = 5 days

    # Rules
    number_of_matches_to_count_points = models.IntegerField(default = 5)
    points_per_kill = models.IntegerField(default = 1)
    points_per_first_place = models.IntegerField(default = 10, verbose_name = "Points for placing - 1st Place")
    points_per_second_place = models.IntegerField(default = 5, verbose_name = "Points for placing - 2nd Place")
    points_per_third_place = models.IntegerField(default = 3, verbose_name = "Points for placing - 3rd Place")

    start_time = models.DateTimeField(default = datetime.now, blank = True)
    end_time = models.DateTimeField(default = datetime.now, blank = True)

    # Competition flag should flip based on time started
    competition_started = models.BooleanField(default = False)
    competition_status = models.IntegerField(default = 3)   # 'Not started': 3, 'Ended': 2, 'In-Progress': 1

    # bg_job
    email_job_created = models.BooleanField(default = False)

    class Meta:
        verbose_name = 'CustomCompetition'
        verbose_name_plural = 'CustomCompetitions'
    
    def __str__(self):
        return str(self.competition_name)


class StaffCustomTeams(models.Model):
    user_id_type = [
        ('acti', 'Activision ID'),
        ('battle', 'Battlenet ID'),
        ('psn', 'Psnet ID'),
        ('xbl', 'XboxLive ID'),
    ]

    team_name = models.CharField(max_length = 100, null = True, unique = True)

    team_captain_email = models.EmailField(max_length = 254, null = True, blank = False) # Null = true populates existing values in db as null - blank = false means the field cannot be blank
    
    team_banner = models.URLField(max_length = 1000, default = 'https://play-lh.googleusercontent.com/r2-_2oE9tU_46_n4GIC21PmqNIqPMoQNRPhfVNnK1v8hmDfA_yLuRwCy_E1cf5Wh4oM')

    team_twitch_stream_user = models.CharField(max_length = 150, null = True, blank = True)

    player_1 = models.CharField(max_length = 100, null = True, blank = True)
    player_1_id_type = models.CharField(max_length = 10, choices = user_id_type, default = 'acti')

    player_2 = models.CharField(max_length = 100, null = True, blank = True)
    player_2_id_type = models.CharField(max_length = 10, choices = user_id_type, default = 'acti')

    player_3 = models.CharField(max_length = 100, null = True, blank = True)
    player_3_id_type = models.CharField(max_length = 10, choices = user_id_type, default = 'acti')

    player_4 = models.CharField(max_length = 100, null = True, blank = True)
    player_4_id_type = models.CharField(max_length = 10, choices = user_id_type, default = 'acti')

    competition = models.ForeignKey(StaffCustomCompetition, on_delete = models.CASCADE, related_name = 'teams')

    data = models.JSONField(default = dict, blank = True)
    data_stats = models.JSONField(default = dict, blank = True)
    data_stats_loaded = models.BooleanField(default = False)
    data_to_render = models.JSONField(default = dict, blank = True)

    score = models.IntegerField(default = 0)

    # email checkin
    email_check_in_sent = models.BooleanField(default = False)

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
    name = models.CharField(max_length = 100, null = True, unique = True, default = 'main_config_controller')
    competitions_page_refresh_time = models.IntegerField(default = 15000)
    competitions_bg_tasks = models.IntegerField(default = 900)
    competitions_dummy_data = models.BooleanField(default = False)

    cod_url_warzone_stats = models.CharField(max_length = 500,  null = True, unique = True)
    cod_url_warzone_matches = models.CharField(max_length = 500,  null = True, unique = True)
    cod_x_rapidapi_key = models.CharField(max_length = 250,  null = True, unique = True)
    cod_x_rapidapi_host = models.CharField(max_length = 250,  null = True, unique = True)

    twitch_api_verfication_client_id = models.CharField(max_length = 100,  null = True, unique = True)
    twitch_api_verfication_client_secret = models.CharField(max_length = 100,  null = True, unique = True)

    class Meta:
        verbose_name = 'ConfigController'
        verbose_name_plural = 'ConfigControllers'
    
    def __str__(self):
        return str("Configuration controller - Do not delete - Do not create more objects")

