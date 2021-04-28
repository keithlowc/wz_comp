from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.get_competitions_all, name = 'get_competitions_all'),
    path('privacy_policy', views.get_privacy_policy, name = 'get_privacy_policy'),

    # User profile patch

    path('profile', views.get_or_create_profile, name = 'get_or_create_profile'),
    path('team/<str:regiment_name>', views.get_regiment_profile, name = 'get_regiment_profile'),
    path('team/<str:regiment_name>/invite/<str:invite_code>', views.regiment_join_confirmation, name = 'regiment_join_confirmation'),
    path('team/<str:regiment_name>/invite/<str:invite_code>/join', views.join_regiment, name = 'join_regiment'),

    # Competition charts
    path('competition/user/chart', views.show_chart, name = 'show_chart'),
    path('competition/recalculate_scores/<str:comp_name>', views.recalculate_scores, name = 'recalculate_scores'),
    path('competition/migratetopastournament/<str:comp_name>', views.migrate_competition_to_past_tournaments, name = 'migrate_competition_to_past_tournaments'),
    
    path('competitions/all', views.get_competitions_all, name = 'get_competitions_all'),
    path('competitions/past/all', views.get_past_tournaments, name = 'get_past_tournaments'),
    path('competition/<str:comp_name>', views.get_competition, name = 'get_competition'),

    path('competition/<str:comp_name>/refresh', views.manually_recalculate_score_once, name = 'manually_recalculate_score_once'),
    path('competition/join/<str:comp_name>', views.join_request_competition, name = 'join_request_competition'),
    path('competition/join/password/<str:comp_name>', views.competition_password_request, name = 'competition_password_request'),

    path('competition/dashboard/<str:comp_name>', views.show_competition_dashboard, name = 'show_competition_dashboard'),
    path('competition/checkin/<str:comp_name>/<uuid:checked_in_uuid>', views.check_in_to_competition, name = 'check_in_to_competition'),
    path('competition/checkin/<str:comp_name>/<str:team_name>/<uuid:checked_in_uuid>', views.check_in, name = 'check_in'),

    path('competition/communication/<str:comp_name>', views.send_competition_email, name = 'send_competition_email'),

    # Verify specific player
    path('cod/verify/player', views.verify_individual_player, name = 'verify_individual_player'),

    # Data remediation
    path('competition/<str:comp_name>/dataremediation', views.remediate_kds, name = 'remediate_kds'),

    # Temporary Rocket League
    path('rocketleague/form/total_upgrade', views.show_rocket_league_form, name = 'show_rocket_league_form'),
]
