from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from .views import IncidentViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'incidents', IncidentViewSet, basename='incident')
urlpatterns = [
    path('', include(router.urls))
]
