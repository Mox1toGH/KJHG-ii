from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ActivityZoneViewSet, LocationMarkerViewSet

app_name = 'locations'

router = DefaultRouter()
router.register(r'markers', LocationMarkerViewSet, basename='marker')
router.register(r'zones', ActivityZoneViewSet, basename='zone')

urlpatterns = [
    path('', include(router.urls)),
]
