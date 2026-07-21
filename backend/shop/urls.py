from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShopItemViewSet, UserItemViewSet

router = DefaultRouter()
router.register(r'items', ShopItemViewSet, basename='shopitem')
router.register(r'user-items', UserItemViewSet, basename='useritem')

urlpatterns = [
    path('', include(router.urls)),
]
