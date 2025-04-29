"""
ASGI config for safemall_api project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
import restapi.routing
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from restapi.middleware import DRFTokenHeaderAuthMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safemall_api.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': DRFTokenHeaderAuthMiddleware(
        URLRouter(
            restapi.routing.websocket_urlpatterns
        )
    )
})
