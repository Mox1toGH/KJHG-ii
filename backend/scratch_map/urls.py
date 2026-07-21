from django.urls import path

from .views import (
    ScratchDiscoveryListView,
    ScratchMapConfigView,
    ScratchMapDiscoverView,
    ScratchMapStatisticsView,
)

urlpatterns = [
    path('discovered/', ScratchDiscoveryListView.as_view(), name='scratch-map-discovered'),
    path('statistics/', ScratchMapStatisticsView.as_view(), name='scratch-map-statistics'),
    path('discover/', ScratchMapDiscoverView.as_view(), name='scratch-map-discover'),
    path('config/', ScratchMapConfigView.as_view(), name='scratch-map-config'),
]
