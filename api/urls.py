from django.urls import include, path
from rest_framework import routers
from . import views


urlpatterns = [
    path('api/match', views.api_matches_overview, name = 'api_matches_overview'),
    path('api/match/all', views.get_all_matches, name = 'get_all_matches'),
    path('api/match/<int:match_id>/', views.get_matches_with_id, name = 'get_matches_with_id'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]