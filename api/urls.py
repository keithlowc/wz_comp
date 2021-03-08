from django.urls import include, path
from rest_framework import routers
from . import views


urlpatterns = [
    
    # Match routes
    path('api/match', views.api_matches_overview, name = 'api_matches_overview'),
    path('api/match/all', views.get_all_matches, name = 'get_all_matches'),
    path('api/match/<int:match_id>/', views.get_matches_with_id, name = 'get_matches_with_id'),

    path('api/match/stats/topkillers/<str:comp_name>', views.get_top_killers, name = 'get_top_killers'),
    path('api/match/stats/topheadshots/<str:comp_name>', views.get_top_headshots, name = 'get_top_headshots'),
    path('api/match/stats/topdeaths/<str:comp_name>', views.get_top_deaths, name = 'get_top_deaths'),
    path('api/match/stats/topdamageperteam/<str:comp_name>', views.get_top_damage_by_team, name = 'get_top_damage_by_team'),
    path('api/match/stats/topdamagetakenperteam/<str:comp_name>', views.get_top_damage_taken_by_team, name = 'get_top_damage_taken_by_team'),
    path('api/match/stats/playertypedistribution/<str:comp_name>', views.get_type_of_players, name = 'get_type_of_players'),

    # Job statuses
    path('api/<str:comp_name>/manually_calculate_job/status', views.get_bg_job_status, name = 'get_bg_job_status'),

    path('api-auth/', include('rest_framework.urls', namespace = 'rest_framework'))
]