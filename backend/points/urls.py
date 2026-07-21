from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PointViewSet

router = DefaultRouter()
router.register(r'', PointViewSet, basename='point')

urlpatterns = [
    path('', include(router.urls)),
]
