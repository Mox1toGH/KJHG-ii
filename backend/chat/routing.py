from django.urls import re_path

from .consumers import ChatConsumer


websocket_urlpatterns = [
    re_path(r'^ws/activities/(?P<activity_id>[a-f0-9\-]+)/chat/$', ChatConsumer.as_asgi()),
]
