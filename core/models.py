from django.db import models
from django.conf import settings
from django.contrib import admin

from django_countries.fields import CountryField

from datetime import datetime

from .validators import validate_competition_name

import uuid

# Custom competitions
class StaffCustomCompetition(models.Model):
    competition_type = [
        ('SQUADS', 'SQUADS'),
        ('TRIOS', 'TRIOS'),
        ('DUOS', 'DUOS'),
        ('SOLOS', 'SOLOS'),
    ]

    competition_name = models.CharField(max_length = 150, null = True, unique = True, validators = [validate_competition_name])

    competition_entry_type = [
        ('Free','Free'),
        ('Paid','Paid'),
    ]

    competition_entry = models.CharField(max_length = 5, choices = competition_entry_type, default = 'Free')

    competition_password = models.CharField(max_length = 15, default = "easy012pass")

    competition_description = models.TextField(default = '')
    competition_type = models.CharField(max_length = 6, choices = competition_type)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, default = 0)
    competition_banner = models.URLField(max_length = 1000, default = 'https://cdn1.dotesports.com/wp-content/uploads/2019/12/16125403/cod38.jpg')
    total_teams_allowed_to_compete = models.IntegerField(default = 20, null = True)

    # Contact Information
    discord_link = models.URLField(max_length = 1000, null = True, blank = True)
    instagram_link = models.URLField(max_length = 1000, null = True, blank = True)
    facebook_link = models.URLField(max_length = 1000, null = True, blank = True)
    twitter_link = models.URLField(max_length = 1000, null = True, blank = True)
    twitch_link = models.URLField(max_length = 1000, null = True, blank = True)

    # Anomaly detection model level
    model_rank_types = [
        ('Gold','Gold'),
        ('Platinum','Platinum'),
        ('Master','Master'),
        ('Legend','Legend'),
        ('Catch_all', 'Catch all'),
    ]

    model_rank = models.CharField(max_length = 9, choices = model_rank_types, default = 'Gold')
    
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
    points_per_fourth_place = models.IntegerField(default = 0, verbose_name = "Points for placing - 4th Place")
    points_per_fifth_place = models.IntegerField(default = 0, verbose_name = "Points for placing - 5th Place")

    start_time = models.DateTimeField(default = datetime.now, blank = True)
    end_time = models.DateTimeField(default = datetime.now, blank = True)

    # Competition flag should flip based on time started
    competition_statuses = [
        ('Not-Started', 'Not-Started'),
        ('In-Progress', 'In-Progress'),
        ('Ended', 'Ended'),
    ]

    competition_status = models.CharField(max_length = 20, choices = competition_statuses, default = 'Not-Started')
    competition_started = models.BooleanField(default = False)

    # Competition closure
    competition_is_closed = models.BooleanField(default = False)
    competition_cover_results = models.BooleanField(default = False)

    # Close inscriptions
    close_inscriptions_started = models.BooleanField(default = False) 

    # Email job
    email_job_created = models.BooleanField(default = False)

    # Statuses for bg jobs
    bg_job_statuses = [
        ('Scheduled', 'Scheduled'),
        ('Started','Started'),
        ('In-Progress', 'In-Progress'),
        ('Completed', 'Completed'),
        ('Not-Running','Not-Running')
    ]

    manually_calculate_bg_job_status = models.CharField(max_length = 12, choices = bg_job_statuses, default = 'Scheduled')

    class Meta:
        verbose_name = 'Custom Competition'
        verbose_name_plural = 'Custom Competitions'
    
    def __str__(self):
        return str(self.competition_name)


class StaffCustomTeams(models.Model):
    user_id_type = [
        ('battle', 'Battlenet ID'),
        ('psn', 'Psnet ID'),
        ('xbl', 'XboxLive ID'),
    ]

    stream_type = [
        ('twitch', 'Twitch'),
        ('facebook', 'Facebook'),
    ]

    team_name = models.CharField(max_length = 100, null = True, unique = True)
    
    team_banner = models.URLField(max_length = 1000, default = 'https://play-lh.googleusercontent.com/r2-_2oE9tU_46_n4GIC21PmqNIqPMoQNRPhfVNnK1v8hmDfA_yLuRwCy_E1cf5Wh4oM')

    team_stream_user = models.CharField(max_length = 150, null = True, blank = True)
    team_stream_user_type = models.CharField(max_length = 10, null = True, choices = stream_type, default = 'twitch')

    team_captain_email = models.EmailField(max_length = 254, null = True, blank = False) # Null = true populates existing values in db as null - blank = false means the field cannot be blank
    player_1 = models.CharField(max_length = 100, null = True, blank = True)
    player_1_id_type = models.CharField(max_length = 10, choices = user_id_type, default = 'battle')
    player_1_kd = models.FloatField(null = True, blank = True)

    player_2_email = models.EmailField(max_length = 254, null = True, blank = True)
    player_2 = models.CharField(max_length = 100, null = True, blank = True)
    player_2_id_type = models.CharField(max_length = 10, choices = user_id_type, default = 'battle')
    player_2_kd = models.FloatField(null = True, blank = True)

    player_3_email = models.EmailField(max_length = 254, null = True, blank = True)
    player_3 = models.CharField(max_length = 100, null = True, blank = True)
    player_3_id_type = models.CharField(max_length = 10, choices = user_id_type, default = 'battle')
    player_3_kd = models.FloatField(null = True, blank = True)

    player_4_email = models.EmailField(max_length = 254, null = True, blank = True)
    player_4 = models.CharField(max_length = 100, null = True, blank = True)
    player_4_id_type = models.CharField(max_length = 10, choices = user_id_type, default = 'battle')
    player_4_kd = models.FloatField(null = True, blank = True)

    competition = models.ForeignKey(StaffCustomCompetition, on_delete = models.CASCADE, related_name = 'teams')

    data = models.JSONField(default = dict, blank = True)
    data_stats = models.JSONField(default = dict, blank = True)
    data_stats_loaded = models.BooleanField(default = False)
    data_to_render = models.JSONField(default = dict, blank = True)

    score = models.IntegerField(default = 0)

    # errors with users
    errors = models.JSONField(default = dict, blank = True)

    # email checkin
    email_check_in_sent = models.BooleanField(default = False)

    # checked in to competition
    checked_in = models.BooleanField(default = False)
    checked_in_uuid = models.UUIDField(default = uuid.uuid4)

    class Meta:
        verbose_name = 'Custom Team'
        verbose_name_plural = 'Custom Teams'
    
    def save(self, *args, **kwargs):

        # Kds are only saved with 2 decimal points
        if self.player_1_kd != None:
            self.player_1_kd = round(self.player_1_kd, 2)

        if self.player_2_kd != None:
            self.player_2_kd = round(self.player_2_kd, 2)

        if self.player_3_kd != None:
            self.player_3_kd = round(self.player_3_kd, 2)
        
        if self.player_4_kd != None:
            self.player_4_kd = round(self.player_4_kd, 2)

        super(StaffCustomTeams, self).save(*args, **kwargs)
    
    def __str__(self):
        return str(self.team_name)


class Player(models.Model):
    competition = models.ManyToManyField(StaffCustomCompetition, related_name = 'players')
    team = models.ManyToManyField(StaffCustomTeams, related_name = 'players')
    user_kd = models.FloatField(null = True)
    user_id = models.CharField(max_length = 100, null = True)
    user_id_type = models.CharField(max_length = 150, null = True)

    class Meta:
        verbose_name = 'Player'
        verbose_name_plural = 'Players'
    
    def save(self, *args, **kwargs):
        self.user_kd = round(self.user_kd, 2)
        super(Player, self).save(*args, **kwargs)
    
    def __str__(self):
        return str(self.user_id)


class Match(models.Model):
    '''
    Contains all matches from current
    tournaments. Data is used to display
    graphs.
    '''

    competition = models.ForeignKey(StaffCustomCompetition, on_delete = models.SET_NULL, null = True, related_name = 'competition')
    team = models.ForeignKey(StaffCustomTeams, on_delete = models.SET_NULL, null = True, related_name = 'matches')
    player = models.ForeignKey(Player, on_delete = models.SET_NULL, null = True, related_name = 'matches')
    match_id = models.CharField(max_length = 300, null = True)
    kills = models.IntegerField(null = True)
    kd = models.FloatField(null = True)
    deaths = models.IntegerField(null = True)
    headshots = models.IntegerField(null = True)
    damage_done = models.FloatField(null = True)
    damage_taken = models.FloatField(null = True)
    placement = models.IntegerField(null = True)
    team_wipes = models.IntegerField(null = True)
    longest_streak = models.IntegerField(null = True)
    utc_start_time = models.CharField(max_length = 100, null = True)
    time_played = models.CharField(max_length = 100, null = True)
    percent_time_moving = models.FloatField(null = True)
    player_kd_at_time = models.FloatField(null = True)
    anomalous_match = models.BooleanField(null = True)
    match_type = models.CharField(max_length = 100, null = True)

    class Meta:
        verbose_name = 'Match'
        verbose_name_plural = 'Matches'

    def save(self, *args, **kwargs):
        self.kd = round(self.kd, 2)
        self.player_kd_at_time = round(self.player_kd_at_time, 2)
        super(Match, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.match_id)


class PastTournaments(models.Model):
    '''
    This table is used to freeze
    already calculated data and 
    to display for those tournaments
    already completed.
    '''

    name = models.CharField(max_length = 150)
    host = models.CharField(max_length = 150, default = '')
    date_ended = models.DateTimeField(default = datetime.now)
    logo = models.URLField(max_length = 500)
    total_teams = models.IntegerField()


    class Meta:
        verbose_name = 'Past Tournament'
        verbose_name_plural = 'Past Tournaments'
    
    def __str__(self):
        return str(self.name)


class PastTeams(models.Model):
    '''
    This table contains all data
    of past teams within
    tournaments - Post completion
    of tournament.
    '''

    tournament = models.ForeignKey(PastTournaments, on_delete = models.CASCADE, null = True, related_name = 'PastTeams')
    name = models.CharField(max_length = 100)

    email_captain = models.EmailField(default = '', null = True, blank = True)
    player_1 = models.CharField(max_length = 100, null = True, blank = True)
    player_1_id_type = models.CharField(max_length = 10, null = True, blank = True)

    player_2_email = models.EmailField(default = '', null = True, blank = True)
    player_2 = models.CharField(max_length = 100, null = True, blank = True)
    player_2_id_type = models.CharField(max_length = 10, null = True, blank = True)

    player_3_email = models.EmailField(default = '', null = True, blank = True)
    player_3 = models.CharField(max_length = 100, null = True, blank = True)
    player_3_id_type = models.CharField(max_length = 10, null = True, blank = True)

    player_4_email = models.EmailField(default = '', null = True, blank = True)
    player_4 = models.CharField(max_length = 100, null = True, blank = True)
    player_4_id_type = models.CharField(max_length = 10, null = True, blank = True)

    points = models.IntegerField()

    class Meta:
        verbose_name = 'Past Team'
        verbose_name_plural = 'Past Teams'
    
    def __str__(self):
        return str(self.name)


class CompetitionCommunicationEmails(models.Model):
    '''
    Contains what ever message is sent
    to users.
    '''

    subject = models.CharField(max_length = 150)
    body = models.TextField()
    date = models.DateTimeField(default = datetime.now)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    competition = models.ForeignKey(StaffCustomCompetition, on_delete = models.CASCADE, related_name = 'emails')

    class Meta:
        verbose_name = 'Competition Communication'
        verbose_name_plural = 'Competition Communications'


class PlayerVerification(models.Model):
    '''
    Model used to display the 
    verification form on the 
    navbar
    '''

    user_id_type = [
        ('battle', 'Battlenet ID'),
        ('psn', 'Psnet ID'),
        ('xbl', 'XboxLive ID'),
    ]
    user_id = models.CharField(max_length = 100, null = True)
    user_id_type = models.CharField(max_length = 10, choices = user_id_type, default = 'battle')


class AbstractModel(models.Model):
    '''
    Model used to display forms with
    different verifications. For 
    instance asking user for password.

    The data should never be saved.
    '''

    password = models.CharField(max_length = 15)


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

    competition_close_inscriptions_bg_active = models.BooleanField(default = True)
    competition_close_inscriptions_before_start = models.IntegerField(default = 60 * 30) # 60 seconds * 30 times = 30 minutes

    competition_email_active = models.BooleanField(default = True)
    competition_email_time_before_start = models.IntegerField(default = 60 * 30) # 60 seconds * 30 times = 30 minutes

    anomaly_detection_active = models.BooleanField(default = True)

    cod_url_warzone_stats = models.CharField(max_length = 500,  null = True, unique = True)
    cod_url_warzone_matches = models.CharField(max_length = 500,  null = True, unique = True)
    cod_x_rapidapi_key = models.CharField(max_length = 250,  null = True, unique = True)
    cod_x_rapidapi_host = models.CharField(max_length = 250,  null = True, unique = True)

    twitch_api_verfication_client_id = models.CharField(max_length = 100,  null = True, unique = True)
    twitch_api_verfication_client_secret = models.CharField(max_length = 100,  null = True, unique = True)

    message_type = [
        ('danger', 'Danger'),
        ('warning', 'Warning'),
        ('info', 'Info'),
    ]

    system_message_type = models.CharField(max_length = 10, choices = message_type, default = 'Info')
    system_message = models.CharField(max_length = 250,  null = True, unique = True, blank = True)

    class Meta:
        verbose_name = 'Application Configuration'
        verbose_name_plural = 'Application Configuration'
    
    def __str__(self):
        return str('Configuration controller - Do not delete - Do not create more objects')


class Analytics(models.Model):
    '''
    Save any sort of data
    that I would like to take a 
    look after. IE: how many requests
    to the api we have done.

    Analytics of the day
    '''
    
    date = models.DateTimeField(default = datetime.now, blank = True)
    amount_of_warzone_api_requests_calls = models.IntegerField(default = 0)

    class Meta:
        verbose_name = 'Application Analytics'
        verbose_name_plural = 'Application Analytics'
    
    def __str__(self):
        return str(self.date)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, null = True, unique = True)
    # profile_name = models.CharField(max_length = 50, null = True, unique = True)
    country = CountryField()
    warzone_tag = models.CharField(max_length = 100, null = True, blank = True, unique = True)
    stream_url = models.URLField()

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return str(self.user)


class Team(models.Model):
    members = models.ManyToManyField(Profile)
    name = models.CharField(max_length = 100, null = True)
    description = models.TextField(max_length = 250)
    invite_code = models.CharField(max_length = 50, default = uuid.uuid4().hex[:6].upper())

    class Meta:
        verbose_name = 'Team'
        verbose_name_plural = 'Teams'
    
    def __str__(self):
        return str(self.name)


# Temporary code
class RocketLeague(models.Model):
    team_name = models.CharField(max_length = 150, null = True, unique = True)
    captain_name = models.CharField(max_length = 100, null = True)
    captain_cellphone_number = models.CharField(max_length = 100, null = True)
    captain_email = models.EmailField()

    platform_type = [
        ('PC', 'PC'),
        ('PSN', 'PSN'),
        ('XBOX', 'XBOX'),
    ]

    rank_type = [
        ('Gold', 'Gold'),
        ('Platinum', 'Platinum'),
    ]

    player_1_id = models.CharField(max_length = 200, null = True, unique = True)
    player_1_platform = models.CharField(max_length = 5, choices = platform_type)
    player_1_rank = models.CharField(max_length = 50, choices = rank_type)

    player_2_id = models.CharField(max_length = 200, null = True, unique = True)
    player_2_platform = models.CharField(max_length = 5, choices = platform_type)
    player_2_rank = models.CharField(max_length = 50, choices = rank_type)

    player_3_id = models.CharField(max_length = 200, null = True, unique = True)
    player_3_platform = models.CharField(max_length = 5, choices = platform_type)
    player_3_rank = models.CharField(max_length = 50, choices = rank_type)

    class Meta:
        verbose_name = 'Rocket League Team'
        verbose_name_plural = 'Rocket League Teams'
    
    def __str__(self):
        return str(self.team_name)



