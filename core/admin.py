from django.contrib import admin

import os

from .models import Profile, Teams, StaffCustomTeams, StaffCustomCompetition, ConfigController

# Register your models here.

admin.site.site_header = 'Codify Manager'
admin.site.site_title = 'Codify Admin Portal'
admin.site.index_title = 'Welcome to Codify Portal'

admin.site.register(Profile)
admin.site.register(Teams)
admin.site.register(ConfigController)

class StaffCustomTeamAdmin(admin.ModelAdmin):
    search_fields = ('team_name',)
    list_filter = ('competition',)

    if 'SERVER' in os.environ:
        fields = (
            'team_name',
            'player_1',
            'player_2',
            'player_3',
            'player_4',
            'competition',
        )
    else:
        fields = (
            'team_name',
            'player_1',
            'player_2',
            'player_3',
            'player_4',
            'competition',
            'data',
            'data_to_score',
            'data_to_render',
            'score',
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
        'player_1',
        'player_2',
        'player_3',
        'player_4',
        'competition',
    )
    extra = 1

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
        return instance

    inlines = [InLineStaffCustomTeam]
    search_fields = ('competition_name',)
    list_filter = ('created_by', 'competition_type',)
    list_display = ('competition_name', 'competition_type',)
    fields = (
        'competition_name',
        'competition_description',
        'competition_banner',
        'competition_type',
        'points_per_kill',
        'points_per_first_place',
        'points_per_second_place',
        'points_per_third_place',
        'start_time',
        'end_time',
    )

admin.site.register(StaffCustomCompetition, StaffCustomCompetitionAdmin)