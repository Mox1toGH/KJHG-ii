from django.urls import path
from .views import ActivityViewSet, ActivityRoleViewSet, ParticipantViewSet, JoinRequestViewSet

app_name = 'activities'

urlpatterns = [
    path('', ActivityViewSet.as_view({'get': 'list', 'post': 'create'}), name='activity-list'),
    path('join-requests/', JoinRequestViewSet.as_view({'get': 'list'}), name='join-request-list'),
    path('join-requests/<uuid:pk>/approve/', JoinRequestViewSet.as_view({'post': 'approve'}), name='join-request-approve'),
    path('join-requests/<uuid:pk>/reject/', JoinRequestViewSet.as_view({'post': 'reject'}), name='join-request-reject'),
    path(
        '<uuid:pk>/',
        ActivityViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}),
        name='activity-detail',
    ),
    path('<uuid:pk>/join/', ActivityViewSet.as_view({'post': 'join'}), name='activity-join'),
    path('<uuid:pk>/leave/', ActivityViewSet.as_view({'post': 'leave'}), name='activity-leave'),
    
    path(
        '<uuid:activity_pk>/roles/',
        ActivityRoleViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='activity-role-list',
    ),
    path(
        '<uuid:activity_pk>/roles/<uuid:pk>/',
        ActivityRoleViewSet.as_view({'patch': 'partial_update', 'delete': 'destroy'}),
        name='activity-role-detail',
    ),
    path('<uuid:activity_pk>/participants/', ParticipantViewSet.as_view({'get': 'list'}), name='activity-participant-list'),
    path('<uuid:activity_pk>/participants/<uuid:pk>/', ParticipantViewSet.as_view({'patch': 'partial_update', 'delete': 'destroy'}), name='activity-participant-detail'),
]
