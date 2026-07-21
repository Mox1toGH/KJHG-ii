import math
import time
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import OperationalError, connection
from .models import ParticipantLocation
from django.utils import timezone
from django.db import transaction
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from notifications.services import publish_activity_notification


def _coordinate(value, *, minimum, maximum, name):
    try:
        coordinate = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationError(f'{name} must be a number.')

    if not coordinate.is_finite() or coordinate < Decimal(str(minimum)) or coordinate > Decimal(str(maximum)):
        raise ValidationError(f'{name} must be between {minimum} and {maximum}.')
    return coordinate


def _optional_float(value, name):
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f'{name} must be a number.')
    if not math.isfinite(number):
        raise ValidationError(f'{name} must be finite.')
    return number


def update_participant_location(participant, latitude, longitude, accuracy=None, heading=None, speed=None):
    latitude = _coordinate(latitude, minimum=-90, maximum=90, name='Latitude')
    longitude = _coordinate(longitude, minimum=-180, maximum=180, name='Longitude')

    defaults = {
        'latitude': latitude,
        'longitude': longitude,
        'accuracy': _optional_float(accuracy, 'Accuracy'),
        'heading': _optional_float(heading, 'Heading'),
        'speed': _optional_float(speed, 'Speed'),
    }

    # Location updates arrive from websocket threads while API requests may
    # also be reading/writing SQLite. Retry only the transient lock case.
    for attempt in range(4):
        try:
            location, _ = ParticipantLocation.objects.update_or_create(
                participant=participant,
                defaults=defaults,
            )
            _process_zone_triggers(participant, latitude, longitude, _optional_float(accuracy, 'Accuracy'))
            return location
        except OperationalError as error:
            if 'locked' not in str(error).lower() or attempt == 3:
                raise
            connection.close()
            time.sleep(0.1 * (attempt + 1))


def _process_zone_triggers(participant, latitude, longitude, accuracy):
    """
    Evaluate zone entry/exit for a participant after their location is updated.

    Notification delivery note
    --------------------------
    This function is called from inside a ``@database_sync_to_async`` thread.
    Calling ``publish_notification`` directly here would invoke
    ``transaction.on_commit`` inside what SQLite/Django treats as a new
    autocommit transaction, which fires the on_commit hook *synchronously*
    before the function even returns.  That in turn calls
    ``async_to_sync(channel_layer.group_send)`` from a sync thread that is
    already inside a ``SyncToAsync`` worker, creating nested event loops that
    slowly exhaust the thread pool and eventually stop delivering messages.

    The fix: wrap the whole block in an explicit ``atomic()`` transaction so
    that ``on_commit`` hooks are deferred until the transaction actually
    commits (after we return), and the channel send happens in the normal
    post-commit signal path — safely outside the current thread.
    """
    if not participant.role_id:
        return

    from django.conf import settings
    from django.db import transaction as db_transaction
    from locations.models import ActivityZone
    from notifications.services import publish_notification
    from .geospatial import point_fully_inside_polygon, point_in_polygon, distance_to_polygon

    accuracy = accuracy if accuracy is not None else 0.0
    entry_accuracy_threshold = getattr(settings, 'ZONE_ENTRY_ACCURACY_THRESHOLD', 75.0)

    # Find zones with triggers in this activity where this participant is the subject
    zones = list(ActivityZone.objects.filter(
        activity_id=participant.activity_id,
        trigger_subject_role_id=participant.role_id
    ).exclude(trigger_action=ActivityZone.TriggerAction.NO_ACTION))

    if not zones:
        return

    current_zone_ids = set(participant.current_zones.values_list('id', flat=True))

    entered_zones = []
    exited_zones = []

    for zone in zones:
        was_inside = zone.id in current_zone_ids

        if not was_inside:
            # ON ENTRY: requires high accuracy AND the entire uncertainty circle
            # to be within the polygon so we don't fire on a boundary straddle.
            if accuracy <= entry_accuracy_threshold:
                if point_fully_inside_polygon(latitude, longitude, accuracy, zone.points):
                    entered_zones.append(zone)
        else:
            # ON EXIT: the point is no longer inside the polygon, AND the
            # distance to the boundary must exceed the accuracy radius so the
            # device is definitively outside (not just straddling the edge).
            is_still_inside = point_in_polygon(latitude, longitude, zone.points)
            if not is_still_inside:
                dist = distance_to_polygon(latitude, longitude, zone.points)
                if dist > accuracy:
                    exited_zones.append(zone)

    if not entered_zones and not exited_zones:
        return

    display_name = (
        ' '.join(filter(None, [participant.user.first_name, participant.user.last_name]))
        or participant.user.username
    )

    # Wrap state mutations + notification creation in a single atomic block so
    # that all on_commit hooks fire together after the transaction commits —
    # avoiding the nested async_to_sync / thread-pool exhaustion problem.
    with db_transaction.atomic():
        if entered_zones:
            participant.current_zones.add(*entered_zones)
            for zone in entered_zones:
                if zone.trigger_action == ActivityZone.TriggerAction.ON_ENTRY and zone.trigger_notify_role_id:
                    notify_user_ids = list(participant.activity.participants.filter(
                        role_id=zone.trigger_notify_role_id
                    ).values_list('user_id', flat=True))
                    if notify_user_ids:
                        publish_notification(
                            user_ids=notify_user_ids,
                            notification_type='zone.entry',
                            title=f'Zone Entry: {zone.name}',
                            body=f"{display_name} entered the zone.",
                            data={
                                'activity_id': str(participant.activity_id),
                                'event': 'zone.entry',
                                'participant_id': str(participant.id),
                                'zone_id': str(zone.id),
                            },
                        )

        if exited_zones:
            participant.current_zones.remove(*exited_zones)
            for zone in exited_zones:
                if zone.trigger_action == ActivityZone.TriggerAction.ON_EXIT and zone.trigger_notify_role_id:
                    notify_user_ids = list(participant.activity.participants.filter(
                        role_id=zone.trigger_notify_role_id
                    ).values_list('user_id', flat=True))
                    if notify_user_ids:
                        publish_notification(
                            user_ids=notify_user_ids,
                            notification_type='zone.exit',
                            title=f'Zone Exit: {zone.name}',
                            body=f"{display_name} exited the zone.",
                            data={
                                'activity_id': str(participant.activity_id),
                                'event': 'zone.exit',
                                'participant_id': str(participant.id),
                                'zone_id': str(zone.id),
                            },
                        )



def activity_tracking_group(activity_id):
    return f'activity_{activity_id}_tracking'


def set_participant_sos(*, participant, active):
    """Set the participant's current emergency state and fan it out to the activity."""
    active = bool(active)
    if participant.sos_active == active:
        return participant

    participant.sos_active = active
    participant.sos_activated_at = timezone.now() if active else None
    participant.save(update_fields=['sos_active', 'sos_activated_at'])

    event = {
        'activity_id': str(participant.activity_id),
        'participant_id': str(participant.id),
        'user': {
            'id': str(participant.user_id),
            'username': participant.user.username,
            'display_name': ' '.join(filter(None, [participant.user.first_name, participant.user.last_name])),
        },
        'active': active,
        'activated_at': participant.sos_activated_at.isoformat().replace('+00:00', 'Z') if participant.sos_activated_at else None,
    }
    transaction.on_commit(lambda: _broadcast_sos(event, participant.user_id))
    if active:
        publish_activity_notification(
            activity=participant.activity,
            notification_type='sos.activated',
            title='🚨 Active SOS in this Activity',
            body=f"{event['user']['display_name'] or event['user']['username']} activated SOS.",
            data={'event': 'sos.activated', 'participant_id': str(participant.id)},
        )
    return participant


def _broadcast_sos(event, exclude_user_id):
    channel_layer = get_channel_layer()
    if channel_layer is not None:
        async_to_sync(channel_layer.group_send)(
            activity_tracking_group(event['activity_id']),
            {'type': 'sos.updated', 'sos': event, 'exclude_user_id': str(exclude_user_id)},
        )
