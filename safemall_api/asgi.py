"""
ASGI config for safemall_api project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
import django

# Set Django settings module before anything else
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safemall_api.settings')
django.setup()  # <-- This must come before importing anything Django-related

# Django and Channels imports
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# Custom routing and middleware
from restapi.middleware import DRFTokenHeaderAuthMiddleware
import restapi.routing


# Application definition
application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
    DRFTokenHeaderAuthMiddleware(
        URLRouter(
            restapi.routing.websocket_urlpatterns
        )
    )
    )
})
