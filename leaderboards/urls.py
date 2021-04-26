from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('leaderboards', views.home, name = 'home'),
    path('leaderboards/records', views.show_records, name = 'show_records')
]
