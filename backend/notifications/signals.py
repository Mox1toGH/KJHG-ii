from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from locations.models import MeetingPoint
from .services import publish_activity_notification


def format_time(value):
    return value.strftime('%H:%M') if hasattr(value, 'strftime') else str(value)[:5]


@receiver(post_save, sender=MeetingPoint)
def meeting_point_created(sender, instance, created, **kwargs):
    if not created:
        return

    transaction.on_commit(lambda: publish_activity_notification(
        activity=instance.marker.activity,
        notification_type='meeting_point.created',
        title=instance.name,
        body=instance.description or f'{instance.marker.name} was set as a meeting point.',
        data={
            'marker_id': str(instance.marker_id),
            'marker_name': instance.marker.name,
            'meeting_point_name': instance.name,
            'meeting_point_description': instance.description,
            'start_time': format_time(instance.start_time),
            'end_time': format_time(instance.end_time),
        },
    ))
