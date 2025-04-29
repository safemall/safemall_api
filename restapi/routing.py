from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/socketserver/<chatroom_name>', consumers.ChatConsumer.as_asgi())
]