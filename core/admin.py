from django.contrib import admin

import os

from .models import Profile, Teams, StaffCustomTeams, StaffCustomCompetition, ConfigController

# from background_task.models import Task

from core.bg_tasks import EmailNotificationSystemJob

# Register your models here.

admin.site.site_header = 'Duelout Manager'
admin.site.site_title = 'Duelout Admin Portal'
admin.site.index_title = 'Welcome to Duelout Portal'

admin.site.register(Profile)
admin.site.register(Teams)
admin.site.register(ConfigController)

# Start config controller



# StaffCustomTeam admin
class StaffCustomTeamAdmin(admin.ModelAdmin):
    def has_view_permission(self, request, obj=None):
        if obj is not None and obj.competition.created_by != request.user:
            if request.user.is_superuser:
                return True
            else:
                return False
        return True

    def has_change_permission(self, request, obj=None):
        if obj is not None and obj.competition.created_by != request.user:
            if request.user.is_superuser:
                return True
            else:
                return False
        return True

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.competition.created_by != request.user:
            if request.user.is_superuser:
                return True
            else:
                return False
        return True

    search_fields = ('team_name',)
    list_display = ('team_name', 'competition', 'score',)
    list_filter = ('competition',)

    if 'SERVER' in os.environ:
        fields = (
            'team_name',
            'team_twitch_stream_user',
            'team_captain_email',
            'team_banner',

            'player_1',
            'player_1_id_type',

            'player_2',
            'player_2_id_type',

            'player_3',
            'player_3_id_type',

            'player_4',
            'player_4_id_type',
            'competition',

            'checked_in',
        )
    else:
        fields = (
            'team_name',
            'team_twitch_stream_user',
            'team_captain_email',
            'team_banner',

            'player_1',
            'player_1_id_type',

            'player_2',
            'player_2_id_type',

            'player_3',
            'player_3_id_type',

            'player_4',
            'player_4_id_type',

            'competition',

            # Non visible
            'data',
            'data_stats',
            'data_to_render',
            'score',

            # Boolean fields
            'data_stats_loaded',
            'email_check_in_sent',

            # Checking in
            'checked_in',
            'checked_in_uuid'
        )

admin.site.register(StaffCustomTeams, StaffCustomTeamAdmin)

class InLineStaffCustomTeam(admin.StackedInline):
    '''
    Allows us to show the staff
    custom teams in the same form
    when creating the competition.
    '''

    model = StaffCustomTeams
    fields = (
        'team_name',
        'team_twitch_stream_user',
        'team_captain_email',
        'team_banner',

        'player_1',
        'player_1_id_type',

        'player_2',
        'player_2_id_type',

        'player_3',
        'player_3_id_type',

        'player_4',
        'player_4_id_type',

        'competition',
    )
    extra = 1

# Competitions admin 
class StaffCustomCompetitionAdmin(admin.ModelAdmin):
    def save_model(self, request, instance, form, change):
        '''
        This allows us to save the 
        user from the request
        as the creator of the model
        '''

        user = request.user 
        instance = form.save(commit=False)
        if not change or not instance.created_by:
            instance.created_by = user
        instance.save()

        # Starting email job 
        # when user save new competition
        # the bg job will run every 1 hour
        # The bg job should not duplicate
        config = ConfigController.objects.get(name = 'main_config_controller')

        if config.competition_email_active:
            competition = StaffCustomCompetition.objects.get(id = instance.id)

            if competition.email_job_created == False:
                email_job = EmailNotificationSystemJob()
                email_job.send_check_in_notification(competition_name = instance.competition_name,
                                                    competition_id = instance.id,
                                                    repeat = 30,
                                                    repeat_until = instance.start_time, 
                                                    verbose_name = "Check-in email - for competition with id: {}".format(instance.id), 
                                                    creator = user)
            else:
                print('Did not create a new BG job')
        return instance
    
    def has_view_permission(self, request, obj=None):
        if obj is not None and obj.created_by != request.user:
            if request.user.is_superuser:
                return True
            else:
                return False
        return True

    def has_change_permission(self, request, obj=None):
        if obj is not None and obj.created_by != request.user:
            if request.user.is_superuser:
                return True
            else:
                return False
        return True

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.created_by != request.user:
            if request.user.is_superuser:
                return True
            else:
                return False
        return True

    inlines = [InLineStaffCustomTeam]
    search_fields = ('competition_name',)
    list_filter = ('created_by', 'competition_type',)
    list_display = ('competition_name', 'competition_type', 'created_by')

    if 'SERVER' in os.environ:
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
                'start_time',
                'end_time',
                )
    else:
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
        'start_time',
        'end_time',

        'competition_started',
        
        # Jobs
        'email_job_created',
        )

admin.site.register(StaffCustomCompetition, StaffCustomCompetitionAdmin)

# Background tasks admin
# The model Task is already registered with 'background_task.BackgroundTasksAdmin'

# class BackgroundTasksAdmin(admin.ModelAdmin):
#     list_filter = ('verbose_name', 'task_name',)

# admin.site.register(Task, BackgroundTasksAdmin)