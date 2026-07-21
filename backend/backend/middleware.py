from urllib.parse import parse_qs
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
import jwt

User = get_user_model()

@database_sync_to_async
def get_user_from_token(token_string):
    try:
        # Validate the token using SimpleJWT
        UntypedToken(token_string)
        # Decode the token payload manually since UntypedToken doesn't expose it nicely in older versions
        decoded_data = jwt.decode(token_string, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_data.get("user_id")
        return User.objects.get(id=user_id)
    except (InvalidToken, TokenError, jwt.DecodeError, User.DoesNotExist):
        return AnonymousUser()

class JWTAuthMiddleware:
    """
    Custom middleware that takes a token from the access_token cookie
    and authenticates the WebSocket connection.
    """
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        cookie_header = headers.get(b'cookie', b'').decode('utf-8')
        
        token = None
        if cookie_header:
            cookies = [cookie.split('=', 1) for cookie in cookie_header.split('; ')]
            cookie_dict = {k: v for k, v in cookies if len((k, v)) == 2}
            token = cookie_dict.get(settings.JWT_COOKIE_ACCESS)
        
        if token:
            scope['user'] = await get_user_from_token(token)
        else:
            scope['user'] = AnonymousUser()

        return await self.inner(scope, receive, send)

def JWTAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(inner)
