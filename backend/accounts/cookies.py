from django.conf import settings
from django.http import HttpResponse


def _max_age(setting_name: str) -> int:
    return int(settings.SIMPLE_JWT[setting_name].total_seconds())


def set_auth_cookies(response: HttpResponse, access: str, refresh: str | None = None) -> None:
    response.set_cookie(
        settings.JWT_COOKIE_ACCESS,
        access,
        max_age=_max_age('ACCESS_TOKEN_LIFETIME'),
        path=settings.JWT_COOKIE_PATH,
        secure=settings.JWT_COOKIE_SECURE,
        httponly=settings.JWT_COOKIE_HTTPONLY,
        samesite=settings.JWT_COOKIE_SAMESITE,
    )

    if refresh is not None:
        response.set_cookie(
            settings.JWT_COOKIE_REFRESH,
            refresh,
            max_age=_max_age('REFRESH_TOKEN_LIFETIME'),
            path=settings.JWT_COOKIE_PATH,
            secure=settings.JWT_COOKIE_SECURE,
            httponly=settings.JWT_COOKIE_HTTPONLY,
            samesite=settings.JWT_COOKIE_SAMESITE,
        )


def delete_auth_cookies(response: HttpResponse) -> None:
    response.delete_cookie(
        settings.JWT_COOKIE_ACCESS,
        path=settings.JWT_COOKIE_PATH,
        samesite=settings.JWT_COOKIE_SAMESITE,
    )
    response.delete_cookie(
        settings.JWT_COOKIE_REFRESH,
        path=settings.JWT_COOKIE_PATH,
        samesite=settings.JWT_COOKIE_SAMESITE,
    )
