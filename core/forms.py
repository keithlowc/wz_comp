from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from crispy_forms.bootstrap import FormActions, FieldWithButtons, StrictButton

from .models import StaffCustomTeams, StaffCustomCompetition, CompetitionCommunicationEmails, PlayerVerification, ConfigController, AbstractModel, RocketLeague, Profile, Regiment, Team

from django.core.exceptions import ValidationError

# Competition patch

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        # exclude = ['player_1']
        fields = ('name', 'player_1', 'player_2', 'player_3', 'player_4')
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(TeamForm, self).__init__(*args, **kwargs)
        profile = Profile.objects.get(user = user)
        members = Regiment.objects.filter(members = profile)[0].members.all()
        self.fields['player_1'].queryset = members
        self.fields['player_2'].queryset = members
        self.fields['player_3'].queryset = members
        self.fields['player_4'].queryset = members
# User profile patch

class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.layout = FormActions(
        #     FieldWithButtons('profile_pic', StrictButton("Set profile pic"))
        # )

    class Meta:
        model = Profile
        fields = ('profile_pic', 'country', 'warzone_tag', 'warzone_tag_type', 'stream_url')
    
        labels = {
            'warzone_tag_type': 'Tag type',
        }

class RegimentForm(forms.ModelForm):
    '''
    Create or edit regiment form
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.layout = FormActions(
        #     FieldWithButtons('regiment_logo', StrictButton("Set profile pic"))
        # )

    class Meta:
        model = Regiment
        fields = ('regiment_logo','name', 'description',)

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
                'team_stream_user',
                'team_stream_user_type',

                'player_1', 
                'player_1_id_type',
                'player_1_kd',

                'player_2_email',
                'player_2', 
                'player_2_id_type', 
                'player_2_kd',

                'player_3_email',
                'player_3', 
                'player_3_id_type',
                'player_3_kd',

                'player_4_email',
                'player_4', 
                'player_4_id_type',
                'player_4_kd',)

        labels = {
            'team_banner': 'Team logo (URL only - Do not change if you do not have logo)',
            'team_captain_email': 'Team Captain Email',
            'team_stream_user': 'Team stream user (DO NOT PUT URL! Username only!)',

            'player_1': 'Player 1 ID - (Battlenet, Psnet or Xbox ID)',
            'player_2': 'Player 2 ID - (Battlenet, Psnet or Xbox ID)',
            'player_3': 'Player 3 ID - (Battlenet, Psnet or Xbox ID)',
            'player_4': 'Player 4 ID - (Battlenet, Psnet or Xbox ID)',

            'player_1_id_type': 'Player 1 - ID type',
            'player_2_id_type': 'Player 2 - ID type',
            'player_3_id_type': 'Player 3 - ID type',
            'player_4_id_type': 'Player 4 - ID type',
        }

class CompetitionPasswordRequestForm(forms.ModelForm):
    '''
    This form is used to request 
    password for the competition
    if set to paid - Never save 
    data into this model.
    '''

    class Meta:
        model = AbstractModel
        fields = ('password',)

        labels = {
            'password': 'Password:'
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

class PlayerVerificationForm(forms.ModelForm):
    '''
    This form is used for the host
    to test any user id and see
    if they are public or not before
    manually adding them to the 
    competition
    '''

    class Meta:
        model = PlayerVerification
        fields = ('user_id',
                  'user_id_type',)
        
        labels = {
            'user_id': 'User ID - (Battlenet, Psnet or Xbox Id)',
            'user_id_type': 'User ID Type',
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
                'team_stream_user',
                'team_stream_user_type',

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
            'team_stream_user': 'Team stream user (Do not put URL except if youtube stream)',

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
                'team_stream_user',
                'team_stream_user_type',

                'team_captain_email',
                'player_1', 
                'player_1_id_type',
                'player_1_kd',

                'player_2_email',
                'player_2', 
                'player_2_id_type',
                'player_2_kd',

                'player_3_email',
                'player_3', 
                'player_3_id_type',
                'player_3_kd',

                'player_4_email',
                'player_4', 
                'player_4_id_type',
                'player_4_kd',

                'competition', 
                'data',
                'data_stats', 
                'data_to_render',
                'errors',
                'score',
                'data_stats_loaded',
                'email_check_in_sent',
                'checked_in',
                'checked_in_uuid',)

        labels = {
            'team_banner': 'Team logo (URL only - Do not change if you do not have logo)',
            'team_captain_email': 'Team Captain Email (Contact Information - Any updates will be via email)',
            'team_stream_user': 'Team stream user (Do not put URL except if youtube stream)',

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
    This form is used to show for
    regular tournament hosts the 
    competition admin page
    '''

    class Meta:
        model = StaffCustomCompetition
        fields = (
                'competition_name',
                'competition_entry',
                'competition_password',
                'competition_description',
                'competition_banner',

                # Contact information
                'discord_link',
                'instagram_link',
                'facebook_link',
                'twitter_link',
                'twitch_link',

                # Model ranks
                'model_rank',

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
            'competition_password': 'Competition password (This password will be needed to sign up)',
            'competition_banner': 'Competition banner (URL only)',
            'start_time': 'Competition Start time',
            'end_time': 'Competition End time',
            'model_rank': 'Select rank for anomaly detection',
            'discord_link': 'Discord link (OPTIONAL)',
            'instagram_link': 'Instagram link (OPTIONAL)',
            'facebook_link': 'Facebook link (OPTIONAL)',
            'twitter_link': 'Twitter link (OPTIONAL)',
            'twitch_link': 'Twitch link (OPTIONAL)',
        }


class CompetitionAdminPageSuperUser(forms.ModelForm):
    '''
    This form is used to be displayed
    on the django admin page for 
    competitions and only superusers
    '''

    # competition_password = forms.CharField(disabled = True)

    class Meta:
        model = StaffCustomCompetition
        fields = (
                'competition_name',
                'competition_entry',
                'competition_password',
                'competition_description',
                'competition_banner',

                # Contact information
                'discord_link',
                'instagram_link',
                'facebook_link',
                'twitter_link',
                'twitch_link',
                
                # Model ranks
                'model_rank',

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

                # ADMIN ONLY FIELDS
                'total_teams_allowed_to_compete',

                'created_by',

                # Competition status
                'competition_status',

                # Job status
                'manually_calculate_bg_job_status',

                # Jobs
                'close_inscriptions_started',
                'email_job_created',

                'competition_started',

                # Cover results
                'competition_cover_results',)
        
        labels = {
            'total_teams_allowed_to_compete': 'Total teams allowed to compete (ADMIN)',
            'competition_password': 'Competition password (Password is required if competition is set to paid)',
            'created_by': 'Competition created by (ADMIN)',
            'competition_banner': 'Competition banner (URL only)',
            'start_time': 'Competition Start time',
            'end_time': 'Competition End time',
            'discord_link': 'Discord link (OPTIONAL)',
            'instagram_link': 'Instagram link (OPTIONAL)',
            'facebook_link': 'Facebook link (OPTIONAL)',
            'twitter_link': 'Twitter link (OPTIONAL)',
            'twitch_link': 'Twitch link (OPTIONAL)',
            'model_rank': 'Select rank for anomaly detection',
            'competition_started': 'Competition has started (ADMIN)',
            'competition_status': 'Competition Status (ADMIN)',
            'competition_cover_results': 'Competition cover results (ADMIN)',
            'email_job_created': 'Email job created (ADMIN)',
            'close_inscriptions_started': 'Close inscriptions job created (ADMIN)',
            'manually_calculate_bg_job_status': 'Manually calculate bg job status (ADMIN)',
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
            'competition_close_inscriptions_bg_active',
            'competition_email_time_before_start',
            'competitions_dummy_data',
            'competition_email_active',
            'anomaly_detection_active',
            'cod_url_warzone_stats',
            'cod_url_warzone_matches',
            'cod_x_rapidapi_key',
            'cod_x_rapidapi_host',
            'twitch_api_verfication_client_id',
            'twitch_api_verfication_client_secret',
            'system_message_type',
            'system_message',
        )
        
        labels = {
            'competition_close_inscriptions_bg_active': 'Competition bg job to close inscriptions',
            'competitions_bg_tasks': 'Competition time to repeat BG jobs (Seconds)',
            'competitions_page_refresh_time': 'Competition Page refresh time (Miliseconds)',
            'competition_email_time_before_start': 'Competition time to fire email job before competition start (Seconds)',
        }


# Temporary Rocket League form

class RocketLeagueForm(forms.ModelForm):
    '''
    Rocket league form for total upgrade
    '''

    class Meta:
        model = RocketLeague
        fields = ('team_name','captain_name','captain_cellphone_number','captain_email',
                    'player_1_id', 'player_1_platform', 'player_1_rank', 'player_2_id',
                    'player_2_platform', 'player_2_rank', 'player_3_id', 'player_3_platform',
                    'player_3_rank')