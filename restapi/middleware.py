from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from django.core.cache import cache
from django.utils.timezone import now


@database_sync_to_async
def get_user_from_token(token_key):
    try:
        token = Token.objects.get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()
    

class DRFTokenHeaderAuthMiddleware(BaseMiddleware):

    async def __call__(self, scope, receive, send):

        headers = dict(scope.get('headers', []))

        auth_header = headers.get(b'authorization', None)
        
        if auth_header:
            try:

                auth_header = auth_header.decode()
                if auth_header.startswith('Token'):
                    token_key = auth_header.split('Token')[1]
                    scope['user'] = await get_user_from_token(token_key)
                else:
                    scope['user'] = AnonymousUser()
            except Exception:
                scope['user'] = AnonymousUser()
        else:
            scope['user'] = AnonymousUser()
        
        return await super().__call__(scope, receive, send)


class ActiveUserCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            cache.set(f'user_online_{request.user.user_chat_id}', now(), timeout=300)# 5 minutes
            return response