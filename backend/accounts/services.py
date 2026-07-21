from dataclasses import dataclass

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.translation import gettext_lazy as _

from .tokens import email_verification_token


@dataclass(frozen=True)
class AuthTokens:
    access: str
    refresh: str


class TokenEmailService:
    @staticmethod
    def encode_uid(user):
        return urlsafe_base64_encode(force_bytes(user.pk))

    @staticmethod
    def decode_user(uidb64):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            return get_user_model().objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            return None

    @classmethod
    def send_email_verification(cls, user):
        uid = cls.encode_uid(user)
        token = email_verification_token.make_token(user)
        link = f'{settings.FRONTEND_URL}/email/verify?uid={uid}&token={token}'
        try:
            send_mail(
                subject=_('Verify your email address'),
                message=_('Confirm your account by opening this link: %(link)s') % {'link': link},
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            # Log error but don't block registration
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Failed to send verification email to {user.email}: {e}')

    @classmethod
    def verify_email(cls, uidb64, token):
        user = cls.decode_user(uidb64)
        if not user or not email_verification_token.check_token(user, token):
            return None
        user.is_email_verified = True
        user.save(update_fields=['is_email_verified'])
        return user

    @classmethod
    def send_password_reset(cls, user):
        uid = cls.encode_uid(user)
        token = default_token_generator.make_token(user)
        link = f'{settings.FRONTEND_URL}/password/reset?uid={uid}&token={token}'
        try:
            send_mail(
                subject=_('Reset your password'),
                message=_('Reset your password by opening this link: %(link)s') % {'link': link},
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            # Log error but don't block password reset
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Failed to send password reset email to {user.email}: {e}')


def blacklist_user_refresh_tokens(user):
    from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

    for token in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=token)


class GoogleAuthService:
    provider = 'google'

    @staticmethod
    def _username_from_email(email):
        User = get_user_model()
        base = email.split('@', 1)[0].replace('+', '-').replace(' ', '-')
        candidate = base[:30] or 'user'
        index = 1
        while User.objects.filter(username__iexact=candidate).exists():
            suffix = f'-{index}'
            candidate = f'{base[:30 - len(suffix)]}{suffix}'
            index += 1
        return candidate

    @classmethod
    def verify_id_token(cls, credential):
        from google.auth.transport import requests as google_requests
        from google.oauth2 import id_token as google_id_token

        audience = getattr(settings, 'GOOGLE_OAUTH_CLIENT_ID', '')
        if not audience:
            raise ValueError(_('GOOGLE_OAUTH_CLIENT_ID is not configured.'))
        return google_id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            audience,
        )

    @classmethod
    @transaction.atomic
    def authenticate(cls, credential):
        payload = cls.verify_id_token(credential)
        email = payload.get('email')
        if not email or not payload.get('email_verified'):
            raise ValueError(_('Google account email is not verified.'))

        User = get_user_model()
        user, created = User.objects.get_or_create(
            email=User.objects.normalize_email(email),
            defaults={
                'username': cls._username_from_email(email),
                'first_name': payload.get('given_name', ''),
                'is_email_verified': True,
                'auth_provider': User.AuthProvider.GOOGLE,
            },
        )
        if not created:
            changed_fields = []
            if not user.is_email_verified:
                user.is_email_verified = True
                changed_fields.append('is_email_verified')
            if user.auth_provider != User.AuthProvider.GOOGLE:
                user.auth_provider = User.AuthProvider.GOOGLE
                changed_fields.append('auth_provider')
            if changed_fields:
                user.save(update_fields=changed_fields)
        return user
