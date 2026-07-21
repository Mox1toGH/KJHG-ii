from django.urls import path

from .views import ActivityChatMessageViewSet

app_name = 'chat'

urlpatterns = [
    path(
        'activities/<uuid:activity_pk>/messages/',
        ActivityChatMessageViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='activity-chat-message-list',
    ),
]
