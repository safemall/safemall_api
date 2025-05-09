from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.core.cache import cache
from django.utils.timezone import now


# Make sure this function is defined before it's used in the middleware class
@database_sync_to_async
def authenticate_token(token_key):
    from django.contrib.auth.models import AnonymousUser
    from rest_framework.authtoken.models import Token
    
    try:
        token = Token.objects.get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()
    

class DRFTokenHeaderAuthMiddleware(BaseMiddleware):
    
    async def __call__(self, scope, receive, send):
        from django.contrib.auth.models import AnonymousUser
        from urllib.parse import parse_qs
        
    
        try:
            #Extract the token from the query string
            query_string = scope.get("query_string", b"").decode()
            token = parse_qs(query_string).get("token",[None])[0]
    
            if token:
                try:
                    token_obj = await authenticate_token(token)
                    scope["user"] = token_obj.user #Attach user to the scope
                except Token.DoesNotExist:
                    scope["user"] =  AnonymousUser()
            else:
                scope['user'] = AnonymousUser()

        except Exception as e:
            import logging
            logging.getLogger("django").error(f"Tokenmiddleware error: {e}")
            scope["user"] = AnonymousUser()

        return await super().__call__(scope,receive, send)
    
        # headers = dict(scope.get('headers', []))

        # auth_header = headers.get(b'authorization', None)
        
        # if auth_header:
        #     try:
        #         auth_header = auth_header.decode()
        #         if auth_header.startswith('Token'):
        #             token_key = auth_header.split('Token')[1].strip()  # Added strip to remove any extra spaces
        #             scope['user'] = await get_user_from_token(token_key)
        #         else:
        #             scope['user'] = AnonymousUser()
        #     except Exception:
        #         scope['user'] = AnonymousUser()
        # else:
        #     scope['user'] = AnonymousUser()
        
        # return await self.inner(scope, receive, send)


class ActiveUserCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            cache.set(f'user_online_{request.user.user_chat_id}', now(), timeout=300)  # 5 minutes
        return response
