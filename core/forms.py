from django import forms

from .models import StaffCustomTeams, StaffCustomCompetition, CompetitionCommunicationEmails, ConfigController

from django.core.exceptions import ValidationError

# Front end forms

class JoinCompetitionRequestForm(forms.ModelForm):
    '''
    This form is used to display 
    normal values needed to be submitted
    by appplication users on the front end.
    '''

    class Meta:
        model = StaffCustomTeams
        fields = ('team_name', 
                'team_banner',
                'team_captain_email',
                'team_twitch_stream_user',

                'player_1', 
                'player_1_id_type', 
                'player_2', 
                'player_2_id_type', 
                'player_3', 
                'player_3_id_type', 
                'player_4', 
                'player_4_id_type',)

        labels = {
            'team_banner': 'Team logo (URL only - Do not change if you do not have logo)',
            'team_captain_email': 'Team Captain Email (Contact Information - Any updates will be via email)',
            'team_twitch_stream_user': 'Team Twitch User (User only - Not URL)',

            'player_1': 'Player 1 Id - (Battlenet, Psnet or Xbox Id)',
            'player_2': 'Player 2 Id - (Battlenet, Psnet or Xbox Id)',
            'player_3': 'Player 3 Id - (Battlenet, Psnet or Xbox Id)',
            'player_4': 'Player 4 Id - (Battlenet, Psnet or Xbox Id)',

            'player_1_id_type': 'Player 1 - Id type',
            'player_2_id_type': 'Player 2 - Id type',
            'player_3_id_type': 'Player 3 - Id type',
            'player_4_id_type': 'Player 4 - Id type',
        }

class EmailCommunicationForm(forms.ModelForm):
    '''
    This form is used to send mass email
    updates to players or participants of the 
    tournament, it also keeps the log of what was 
    sent before.
    '''

    class Meta:
        model = CompetitionCommunicationEmails
        fields = ('subject',
                  'body',)

        labels = {
            'subject': 'Subject',
            'body': 'Body'
        }


# ADMIN PAGE FORMS

class TeamFormAdminPage(forms.ModelForm):
    '''
    This form is used to display 
    normal values needed to be submitted
    by appplication users and tournament
    hosts who are not super users.
    '''

    class Meta:
        model = StaffCustomTeams
        fields = ('team_name', 
                'team_banner',
                'team_captain_email',
                'team_twitch_stream_user',

                'player_1', 
                'player_1_id_type', 
                'player_2', 
                'player_2_id_type', 
                'player_3', 
                'player_3_id_type', 
                'player_4', 
                'player_4_id_type',
                'checked_in')

        labels = {
            'team_banner': 'Team logo (URL only - Do not change if you do not have logo)',
            'team_captain_email': 'Team Captain Email (Contact Information - Any updates will be via email)',
            'team_twitch_stream_user': 'Team Twitch User (User only - Not URL)',

            'player_1': 'Player 1 Id - (Battlenet, Psnet or Xbox Id)',
            'player_2': 'Player 2 Id - (Battlenet, Psnet or Xbox Id)',
            'player_3': 'Player 3 Id - (Battlenet, Psnet or Xbox Id)',
            'player_4': 'Player 4 Id - (Battlenet, Psnet or Xbox Id)',

            'player_1_id_type': 'Player 1 - Id type',
            'player_2_id_type': 'Player 2 - Id type',
            'player_3_id_type': 'Player 3 - Id type',
            'player_4_id_type': 'Player 4 - Id type',
            'checked_in': 'Check in team?',
        }


class TeamFormAdminPageSuperUser(forms.ModelForm):
    '''
    This form is used to display
    specific hidden values in the 
    admin page, unless user is 
    super user
    '''

    class Meta:
        model = StaffCustomTeams
        fields = ('team_name', 
                'team_banner',
                'team_captain_email',
                'team_twitch_stream_user',

                'player_1', 
                'player_1_id_type', 
                'player_2', 
                'player_2_id_type', 
                'player_3', 
                'player_3_id_type', 
                'player_4', 
                'player_4_id_type',

                'competition', 
                'data',
                'data_stats', 
                'data_to_render',
                'score',
                'data_stats_loaded',
                'email_check_in_sent',
                'checked_in',
                'checked_in_uuid',)

        labels = {
            'team_banner': 'Team logo (URL only - Do not change if you do not have logo)',
            'team_captain_email': 'Team Captain Email (Contact Information - Any updates will be via email)',
            'team_twitch_stream_user': 'Team Twitch User (User only - Not URL)',

            'player_1': 'Player 1 Id - (Battlenet, Psnet or Xbox Id)',
            'player_2': 'Player 2 Id - (Battlenet, Psnet or Xbox Id)',
            'player_3': 'Player 3 Id - (Battlenet, Psnet or Xbox Id)',
            'player_4': 'Player 4 Id - (Battlenet, Psnet or Xbox Id)',

            'player_1_id_type': 'Player 1 - Id type',
            'player_2_id_type': 'Player 2 - Id type',
            'player_3_id_type': 'Player 3 - Id type',
            'player_4_id_type': 'Player 4 - Id type',

            'checked_in': 'Check in team?',

            'competition': 'Competition (ADMIN)',
            'data': 'Data (ADMIN)',
            'data_stats': 'Data stats (ADMIN)',
            'data_to_render': 'Data to render (ADMIN)',
            'score': 'Team Score (ADMIN)',
            'data_stats_loaded': 'Data stats loaded (ADMIN)',
            'email_check_in_sent': 'Email check in sent? (ADMIN)',
            'checked_in_uuid': 'Check in UUID (ADMIN)',
        }


class CompetitionAdminPage(forms.ModelForm):
    '''
    This form is used to send mass email
    updates to players or participants of the 
    tournament, it also keeps the log of what was 
    sent before.
    '''

    class Meta:
        model = StaffCustomCompetition
        fields = (
                'competition_name',
                'competition_description',
                'competition_banner',
                'total_teams_allowed_to_compete',

                # Contact information
                'discord_link',
                'instagram_link',
                'facebook_link',
                'twitter_link',
                'twitch_link',

                # Verification values
                'cod_kd_minimum_per_player_verification',
                'cod_kd_maximum_per_player_verification',
                'cod_verification_total_games_played',
                'cod_verification_total_time_played',

                'competition_type',
                'number_of_matches_to_count_points',
                'points_per_kill',
                'points_per_first_place',
                'points_per_second_place',
                'points_per_third_place',
                'points_per_fourth_place',
                'points_per_fifth_place',
                'start_time',
                'end_time',
                'competition_is_closed',
                )
        
        labels = {
            'competition_banner': 'Competition banner (URL only)',
            'start_time': 'Competition Start time',
            'end_time': 'Competition End time',
            'discord_link': 'Discord link (OPTIONAL)',
            'instagram_link': 'Instagram link (OPTIONAL)',
            'facebook_link': 'Facebook link (OPTIONAL)',
            'twitter_link': 'Twitter link (OPTIONAL)',
            'twitch_link': 'Twitch link (OPTIONAL)',
        }


class CompetitionAdminPageSuperUser(forms.ModelForm):
    '''
    This form is used to send mass email
    updates to players or participants of the 
    tournament, it also keeps the log of what was 
    sent before.
    '''

    class Meta:
        model = StaffCustomCompetition
        fields = (
                'competition_name',
                'competition_description',
                'competition_banner',
                'total_teams_allowed_to_compete',
                'created_by',

                # Contact information
                'discord_link',
                'instagram_link',
                'facebook_link',
                'twitter_link',
                'twitch_link',

                # Verification values
                'cod_kd_minimum_per_player_verification',
                'cod_kd_maximum_per_player_verification',
                'cod_verification_total_games_played',
                'cod_verification_total_time_played',

                'competition_type',
                'number_of_matches_to_count_points',
                'points_per_kill',
                'points_per_first_place',
                'points_per_second_place',
                'points_per_third_place',
                'points_per_fourth_place',
                'points_per_fifth_place',
                'start_time',
                'end_time',
                'competition_is_closed',

                'competition_started',
                
                # Jobs
                'email_job_created')
        
        labels = {
            'created_by': 'Competition created by (ADMIN)',
            'competition_banner': 'Competition banner (URL only)',
            'start_time': 'Competition Start time',
            'end_time': 'Competition End time',
            'discord_link': 'Discord link (OPTIONAL)',
            'instagram_link': 'Instagram link (OPTIONAL)',
            'facebook_link': 'Facebook link (OPTIONAL)',
            'twitter_link': 'Twitter link (OPTIONAL)',
            'twitch_link': 'Twitch link (OPTIONAL)',
        }


class ConfigControllerAdminPage(forms.ModelForm):
    '''
    This form controls how we view the 
    application configuration settings.
    '''

    class Meta:
        model = ConfigController

        fields = (
            'name',
            'competitions_page_refresh_time',
            'competitions_bg_tasks',
            'competitions_dummy_data',
            'competition_email_active',
            'competition_email_time_to_repeat',
            'cod_url_warzone_stats',
            'cod_url_warzone_matches',
            'cod_x_rapidapi_key',
            'cod_x_rapidapi_host',
            'twitch_api_verfication_client_id',
            'twitch_api_verfication_client_secret',
        )
        
        labels = {
            'competitions_page_refresh_time': 'Competition Page refresh time (Miliseconds)',
            'competition_email_time_to_repeat': 'Competition time to repeat email job (Seconds)',
        }
