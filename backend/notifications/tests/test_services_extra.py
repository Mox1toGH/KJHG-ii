import pytest
import uuid
from django.core import mail
from unittest.mock import patch

from notifications.models import Notification
from notifications.services import enrich_notification_data, publish_notification, send_email_notification
from tests.factories import ActivityFactory, NotificationFactory, UserFactory


@pytest.mark.django_db
def test_enrich_notification_data_resolves_activity_and_ignores_invalid_ids():
    activity = ActivityFactory()
    notification = NotificationFactory(data={'activity_id': str(activity.id), 'participant_id': str(uuid.uuid4())})
    data = enrich_notification_data(notification)
    assert data['activity'] == activity
    assert data['activity_type'] == 'Activity'
    assert 'participant' not in data


@pytest.mark.django_db
def test_send_email_notification_respects_disabled_preferences():
    user = UserFactory(email='person@example.com')
    user.notification_preferences.email_enabled = False
    user.notification_preferences.save(update_fields=['email_enabled'])
    notification = NotificationFactory(user=user)
    assert send_email_notification(notification) is False
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_publish_notification_deduplicates_recipient_ids():
    first = UserFactory()
    second = UserFactory()
    notifications = publish_notification(
        user_ids=[first.id, first.id, second.id],
        notification_type='test.created',
        title='Test',
        body='Body',
    )
    assert {notification.user_id for notification in notifications} == {first.id, second.id}
    assert Notification.objects.filter(type='test.created').count() == 2
