from django.contrib import admin

from .models import Profile, Teams, StaffCustomTeams, StaffCustomCompetition, ConfigController

# Register your models here.

admin.site.register(Profile)
admin.site.register(Teams)
admin.site.register(StaffCustomTeams)
admin.site.register(StaffCustomCompetition)
admin.site.register(ConfigController)