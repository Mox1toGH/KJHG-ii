"""Use-case services for creating and managing notifications."""

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Notification


def user_notification_group(user_id):
    return f'user_{user_id}_notifications'


def notification_message(notification):
    return {
        'id': str(notification.id),
        'type': notification.type,
        'title': notification.title,
        'body': notification.body,
        'data': notification.data,
        'created_at': notification.created_at.isoformat().replace('+00:00', 'Z'),
        'read_at': notification.read_at.isoformat().replace('+00:00', 'Z') if notification.read_at else None,
        'is_read': notification.is_read,
    }


def push_notification(notification):
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    async_to_sync(channel_layer.group_send)(
        user_notification_group(notification.user_id),
        {'type': 'notification.created', 'notification': notification_message(notification)},
    )


def create_notification(*, user, notification_type, title, body, data=None):
    notification = Notification.objects.create(
        user=user,
        type=notification_type,
        title=title,
        body=body,
        data=data or {},
    )
    transaction.on_commit(lambda: push_notification(notification))
    transaction.on_commit(lambda: send_email_notification(notification))
    return notification


def publish_notification(*, user_ids, notification_type, title, body, data=None):
    """Persist and deliver one notification for each distinct recipient."""
    from django.contrib.auth import get_user_model

    users = get_user_model().objects.filter(id__in=set(user_ids))
    return [create_notification(
        user=user,
        notification_type=notification_type,
        title=title,
        body=body,
        data=data,
    ) for user in users]


def publish_activity_notification(*, activity, notification_type, title, body, data=None):
    user_ids = activity.participants.values_list('user_id', flat=True)
    return publish_notification(
        user_ids=user_ids,
        notification_type=notification_type,
        title=title,
        body=body,
        data={'activity_id': str(activity.id), **(data or {})},
    )


def mark_as_read(*, notification, user):
    if notification.user_id != user.id:
        return notification
    if notification.read_at is None:
        notification.read_at = timezone.now()
        notification.save(update_fields=['read_at'])
    return notification


def mark_all_as_read(*, user):
    return Notification.objects.active().filter(user=user, read_at__isnull=True).update(read_at=timezone.now())


def soft_delete(*, notification, user):
    if notification.user_id != user.id:
        return False
    notification.deleted_at = timezone.now()
    notification.save(update_fields=['deleted_at'])
    return True


def clear_all(*, user):
    return Notification.objects.active().filter(user=user).update(deleted_at=timezone.now())


def enrich_notification_data(notification):
    """Enrich notification data with actual database objects instead of IDs."""
    from activities.models import Activity, Participant
    from locations.models import LocationMarker, ActivityZone
    
    enriched_data = notification.data.copy()
    
    # Load Activity if activity_id is present
    if 'activity_id' in enriched_data:
        try:
            activity = Activity.objects.get(id=enriched_data['activity_id'])
            enriched_data['activity'] = activity
            enriched_data['activity_type'] = 'Activity'
        except (Activity.DoesNotExist, ValueError) as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not load activity {enriched_data.get('activity_id')}: {e}")
    
    # Load Participant if participant_id is present
    if 'participant_id' in enriched_data:
        try:
            participant = Participant.objects.get(id=enriched_data['participant_id'])
            enriched_data['participant'] = participant
            enriched_data['participant_type'] = 'Participant'
        except (Participant.DoesNotExist, ValueError) as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not load participant {enriched_data.get('participant_id')}: {e}")
    
    # Load ActivityZone if zone_id is present
    if 'zone_id' in enriched_data:
        try:
            zone = ActivityZone.objects.get(id=enriched_data['zone_id'])
            enriched_data['zone'] = zone
            enriched_data['zone_type'] = 'ActivityZone'
        except (ActivityZone.DoesNotExist, ValueError) as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not load zone {enriched_data.get('zone_id')}: {e}")
    
    # Load LocationMarker if marker_id is present
    if 'marker_id' in enriched_data:
        try:
            marker = LocationMarker.objects.get(id=enriched_data['marker_id'])
            enriched_data['marker'] = marker
            enriched_data['marker_type'] = 'LocationMarker'
        except (LocationMarker.DoesNotExist, ValueError) as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not load marker {enriched_data.get('marker_id')}: {e}")
    
    return enriched_data


def send_email_notification(notification):
    """Send an email notification using HTML template."""
    # Email notifications disabled
    return False
