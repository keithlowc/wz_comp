from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    # path('send_mail', views.test_send_mail, name = 'test_send_mail'),
    path('', views.get_competitions_all, name = 'get_competitions_all'),

    # Competition charts
    path('competition/chart/stats/<str:team_name>/<str:user>/<str:key>', views.chart_stats_key, name = 'chart_stats_key'),
    path('competition/user/chart', views.show_chart, name = 'show_chart'),
    path('competition/recalculate_scores/<str:comp_name>', views.recalculate_scores, name = 'recalculate_scores'),
    
    path('competitions/all', views.get_competitions_all, name = 'get_competitions_all'),
    path('competition/<str:comp_name>', views.get_competition, name = 'get_competition'),
    path('competition/<str:comp_name>/refresh', views.manually_recalculate_score_once, name = 'manually_recalculate_score_once'),

    # Stage 1
    path('competition/join/<str:comp_name>', views.join_request_competition, name = 'join_request_competition'),

    # Stage 2

    # Stage 3

    # Old application routes
    path('profile/', views.view_profile, name = 'view_profile'),
    path('profile/edit', views.edit_profile, name = 'edit_profile'),
    path('profile/refresh', views.refresh_profile, name = 'refresh_profile'),
    path('profile/search/<str:tag>', views.get_profile, name = 'get_profile'),

    path('team/myteams', views.view_teams, name = 'view_teams'),
    path('team/search/<str:team_name>', views.view_team, name = 'view_team'),
    path('team/create', views.create_team, name = 'create_team'),
    path('team/edit/<str:team_name>', views.edit_team, name = 'edit_team'),
    path('team/delete/<str:team_name>', views.delete_team, name = 'delete_team'),
    path('team/leave/<str:team_name>', views.leave_team, name = 'leave_team'),
]
