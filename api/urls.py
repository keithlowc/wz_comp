from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'allmatches', views.AllMatchesViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/get/match/<int:match_id>/', views.get_match, name = 'get_match'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]