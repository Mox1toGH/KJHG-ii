from django.urls import path

from .consumers import ScratchMapConsumer


websocket_urlpatterns = [
    path('ws/scratch-map/', ScratchMapConsumer.as_asgi()),
]
