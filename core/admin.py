from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
import csv, datetime

from .models import StaffCustomTeams, Match, Player, StaffCustomCompetition, CompetitionCommunicationEmails, ConfigController, Analytics, PastTournaments, PastTeams
from .forms import TeamFormAdminPage, TeamFormAdminPageSuperUser, CompetitionAdminPage, CompetitionAdminPageSuperUser, ConfigControllerAdminPage

# from background_task.models import Task

from core.bg_tasks import EmailNotificationSystemJob, competition_close_inscriptions

# Register your models here.

admin.site.site_header = 'Duelout Manager'
admin.site.site_title = 'Duelout Admin Portal'
admin.site.index_title = 'Welcome to Duelout Portal'

admin.site.register(Analytics)

# StaffCustomTeam admin
class StaffCustomTeamAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        '''
        Controls the fields we display 
        on admin page
        '''

        if request.user.is_superuser:
            kwargs['form'] = TeamFormAdminPageSuperUser
        else:
            kwargs['form'] = TeamFormAdminPage
        
        return super().get_form(request, obj, **kwargs)

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
    list_display = ('team_name', 'competition', 'score', 'checked_in')
    list_filter = ('competition',)

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
        'team_stream_user',
        'team_stream_user_type',
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

        'checked_in',
    )
    extra = 1

# Competitions admin 
class StaffCustomCompetitionAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        '''
        Controls the fields we display 
        on admin page
        '''

        if request.user.is_superuser:
            kwargs['form'] = CompetitionAdminPageSuperUser
        else:
            kwargs['form'] = CompetitionAdminPage
        
        return super().get_form(request, obj, **kwargs)

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
        competition = StaffCustomCompetition.objects.get(id = instance.id)
        competition_start_time = competition.start_time

        if config.competition_close_inscriptions_bg_active:
            if competition.close_inscriptions_started == False:

                competition_close_inscriptions(competition_id = instance.id,
                                               schedule = competition_start_time - datetime.timedelta(seconds = config.competition_close_inscriptions_before_start))
                competition.close_inscriptions_started = True

        if config.competition_email_active:
            if competition.email_job_created == False:

                email_job = EmailNotificationSystemJob()
                email_job.send_check_in_notification(competition_name = instance.competition_name,
                                                     competition_id = instance.id,
                                                     schedule = competition_start_time - datetime.timedelta(seconds = config.competition_email_time_before_start),
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

    def export_tournament_data(self, request, queryset):
        '''
        Allows the super_user to download
        or export their tournament data
        '''

        if not request.user.is_superuser:
            raise PermissionDenied
        else:
            try:
                response = HttpResponse(content_type = 'text/csv')
                response['Content-Disposition'] = 'attachment; filename="tournament_data.csv"'
                writer = csv.writer(response)

                competion_header_rows = ['competition_name','competition_description','competition_type',
                                        'created_by','competition_banner','total_teams_allowed_to_compete',
                                        'discord_link','instagram_link','facebook_link',
                                        'twitter_link','twitch_link','cod_kd_maximum_per_player_verification',
                                        'cod_kd_minimum_per_player_verification','cod_verification_total_games_played',
                                        'cod_verification_total_time_played','number_of_matches_to_count_points',
                                        'points_per_kill','points_per_first_place','points_per_second_place',
                                        'points_per_third_place','points_per_fourth_place','points_per_fifth_place',
                                        'start_time','end_time']
                
                team_header_rows = ['team_name','team_captain_email','team_banner',
                                    'team_stream_user','team_stream_user_type','player_1',
                                    'player_1_id_type','player_2','player_2_id_type',
                                    'player_3','player_3_id_type','player_4','player_4_id_type','competition']

                competitions = queryset

                for index, competition in enumerate(competitions):

                    # Write rows for competition
                    writer.writerow(competion_header_rows)
                    writer.writerow([competition.competition_name, 
                                    competition.competition_description, 
                                    competition.competition_type,
                                    competition.created_by, 
                                    competition.competition_banner, 
                                    competition.total_teams_allowed_to_compete,
                                    competition.discord_link, 
                                    competition.instagram_link,
                                    competition.facebook_link, 
                                    competition.twitter_link, 
                                    competition.twitch_link, 
                                    competition.cod_kd_maximum_per_player_verification,
                                    competition.cod_kd_minimum_per_player_verification, 
                                    competition.cod_verification_total_games_played, 
                                    competition.cod_verification_total_time_played,
                                    competition.number_of_matches_to_count_points, 
                                    competition.points_per_kill, 
                                    competition.points_per_first_place,
                                    competition.points_per_second_place, 
                                    competition.points_per_third_place, 
                                    competition.points_per_fourth_place,
                                    competition.points_per_fifth_place, 
                                    competition.start_time, 
                                    competition.end_time,])

                    # Write rows for teams
                    writer.writerow(team_header_rows)
                    teams = competition.teams.all()

                    for team in teams:
                        writer.writerow([team.team_name,
                                        team.team_captain_email,
                                        team.team_banner,
                                        team.team_stream_user,
                                        team.team_stream_user_type,
                                        team.player_1,
                                        team.player_1_id_type,
                                        team.player_2,
                                        team.player_2_id_type,
                                        team.player_3,
                                        team.player_3_id_type,
                                        team.player_4,
                                        team.player_4_id_type,
                                        team.competition,])
                    
                self.message_user(request, 'Succesfully downloaded files!', messages.SUCCESS)
                return response

            except Exception as e:
                self.message_user(request, 'There was an issue while downloading the file', messages.SUCCESS)
                return True

    inlines = [InLineStaffCustomTeam]
    search_fields = ('competition_name',)
    list_filter = ('created_by', 'competition_type',)
    list_display = ('competition_name', 'competition_type', 'created_by', 'start_time')
    actions = ['export_tournament_data', ]
    save_as = True # Allows us to make a copy of the current competition

admin.site.register(StaffCustomCompetition, StaffCustomCompetitionAdmin)

class MatchAdmin(admin.ModelAdmin):
    search_fields = ('team', 'match_id', 'player',)
    list_display = ('competition', 'team', 'player', 'match_id', 
                    'kills', 'kd', 'deaths', 'headshots', 'damage_done', 
                    'damage_taken', 'placement', 'team_wipes', 'longest_streak',
                    'utc_start_time', 'time_played', 'percent_time_moving', 'player_kd_at_time',)
    list_filter = ('team',)

admin.site.register(Match, MatchAdmin)


# Past tournament admin
class InLinePastTeams(admin.StackedInline):
    '''
    Allows us to show the staff
    custom teams in the same form
    when creating the competition.
    '''

    model = PastTeams
    fields = (
        'name',
        'email_captain',
        'player_1',
        'player_1_id_type',

        'player_2_email',
        'player_2',
        'player_2_id_type',

        'player_3_email',
        'player_3',
        'player_3_id_type',

        'player_4_email',
        'player_4',
        'player_4_id_type',

        'points',
    )
    extra = 1


class PastTournamentsAdmin(admin.ModelAdmin):
    def export_contact_information(self, request, queryset):
        '''
        Exports all emails from past tournaments.
        '''

        if not request.user.is_superuser:
            raise PermissionDenied
        else:
            try:
                response = HttpResponse(content_type = 'text/csv')
                response['Content-Disposition'] = 'attachment; filename="contact_information.csv"'
                writer = csv.writer(response)

                header_rows = ['email']
                writer.writerow(header_rows)

                tournaments = queryset

                for tournament in tournaments:
                    teams = tournament.PastTeams.all()
                    for team in teams:
                        try:
                            writer.writerow([team.email_captain])
                            writer.writerow([team.player_2_email])
                            writer.writerow([team.player_3_email])
                            writer.writerow([team.player_4_email])
                        except:
                            pass

                self.message_user(request, 'Succesfully downloaded files!', messages.SUCCESS)
                return response

            except Exception as e:
                self.message_user(request, 'There was an issue while downloading the file', messages.SUCCESS)
                return True

    inlines = [InLinePastTeams]
    search_fields = ('name',)
    list_display = ('name', 'total_teams',)
    actions = ['export_contact_information', ]

admin.site.register(PastTournaments, PastTournamentsAdmin)

class PlayerAdmin(admin.ModelAdmin):
    search_fields = ('user_id',)
    list_display = ('user_id', 'user_id_type', 'user_kd',)

admin.site.register(Player, PlayerAdmin)

# Competition communications
class CompetitionCommunicationEmailsAdmin(admin.ModelAdmin):
    search_fields = ('competition',)
    list_filter = ('competition', 'created_by')
    list_display = ('competition', 'subject', 'date', 'created_by')

admin.site.register(CompetitionCommunicationEmails, CompetitionCommunicationEmailsAdmin)


# Application configuration
class ConfigControllerAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        '''
        Controls the fields we display 
        on admin page
        '''

        kwargs['form'] = ConfigControllerAdminPage
        
        return super().get_form(request, obj, **kwargs)

admin.site.register(ConfigController, ConfigControllerAdmin)

