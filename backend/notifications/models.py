import os

import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


def get_default_email_enabled():
    return os.getenv('DEFAULT_EMAIL_NOTIFICATIONS_ENABLED', 'False').lower() in ('true', '1', 'yes')


def get_default_in_app_enabled():
    return os.getenv('DEFAULT_IN_APP_NOTIFICATIONS_ENABLED', 'True').lower() in ('true', '1', 'yes')


class NotificationQuerySet(models.QuerySet):
    def active(self):
        return self.filter(deleted_at__isnull=True)


class Notification(models.Model):
    """A durable, user-scoped notification with an extensible JSON payload."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications', verbose_name=_('User'))
    type = models.CharField(max_length=100, verbose_name=_('Type'))
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    body = models.TextField(verbose_name=_('Body'))
    data = models.JSONField(default=dict, blank=True, verbose_name=_('Data'))
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Read at'))
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Deleted at'))

    objects = NotificationQuerySet.as_manager()

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'read_at']),
        ]

    @property
    def is_read(self):
        return self.read_at is not None


class UserNotificationPreferences(models.Model):
    """User preferences for notification delivery channels."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences',
        verbose_name=_('User')
    )
    email_enabled = models.BooleanField(default=get_default_email_enabled, verbose_name=_('Email enabled'))
    in_app_enabled = models.BooleanField(default=get_default_in_app_enabled, verbose_name=_('In-app enabled'))

    class Meta:
        verbose_name = _('User Notification Preferences')
        verbose_name_plural = _('User Notification Preferences')

    def __str__(self):
        return f"{self.user.username} - Email: {self.email_enabled}, In-App: {self.in_app_enabled}"

