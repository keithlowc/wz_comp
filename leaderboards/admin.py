from django.contrib import admin

from .models import Teams
# Register your models here.

class TeamsAdmin(admin.ModelAdmin):
    search_fields = ('team_name',)
    list_display = ('team_name', 'kills', 'record_mode')
    list_filter = ('record_mode',)

admin.site.register(Teams, TeamsAdmin)