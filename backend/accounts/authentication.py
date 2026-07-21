from typing import Optional

from django.conf import settings
from rest_framework import exceptions
from rest_framework.authentication import CSRFCheck
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken


class CookieJWTAuthentication(JWTAuthentication):
    """
    Authenticate with a Bearer token first, then fall back to the access cookie.
    CSRF is enforced when a cookie token is used.
    """

    def authenticate(self, request: Request):
        header = self.get_header(request)
        if header is not None:
            raw_token = self.get_raw_token(header)
            if raw_token is None:
                return None
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token

        raw_token = self.get_cookie_token(request)
        if raw_token is None:
            return None

        # If the cookie token is invalid or expired, treat the request as
        # anonymous so that AllowAny views (e.g. Google login, token refresh)
        # can still proceed instead of receiving a hard 401.
        try:
            self.enforce_csrf(request)
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except (AuthenticationFailed, InvalidToken, exceptions.PermissionDenied):
            return None

    def get_cookie_token(self, request: Request) -> Optional[str]:
        return request.COOKIES.get(settings.JWT_COOKIE_ACCESS)

    def enforce_csrf(self, request: Request) -> None:
        def dummy_get_response(request):
            return None

        check = CSRFCheck(dummy_get_response)
        check.process_request(request)
        reason = check.process_view(request, None, (), {})
        if reason:
            raise exceptions.PermissionDenied(f'CSRF Failed: {reason}')
