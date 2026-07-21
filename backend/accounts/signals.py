from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User, UserStatus


@receiver(post_save, sender=User)
def create_default_statuses(sender, instance, created, **kwargs):
    if created:
        UserStatus.objects.bulk_create([
            UserStatus(user=instance, name=name)
            for name in UserStatus.DEFAULT_NAMES
        ])


@receiver(post_save, sender=User)
def create_notification_preferences(sender, instance, created, **kwargs):
    if created:
        from notifications.models import UserNotificationPreferences
        UserNotificationPreferences.objects.get_or_create(user=instance)
