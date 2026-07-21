from unittest.mock import patch

import pytest
from asgiref.sync import async_to_sync
from django.contrib.auth.models import AnonymousUser
from django.db import transaction
from django.utils import timezone
from unittest.mock import AsyncMock, Mock

from notifications.consumers import NotificationConsumer
from notifications.models import Notification
from notifications.services import (
    clear_all, create_notification, mark_all_as_read, mark_as_read, soft_delete,
)
from tests.factories import NotificationFactory, UserFactory


@pytest.mark.django_db
def test_notification_lifecycle_is_user_scoped():
    user = UserFactory()
    other = UserFactory()
    notification = NotificationFactory(user=user)
    other_notification = NotificationFactory(user=other)

    assert mark_as_read(notification=notification, user=other).read_at is None
    mark_as_read(notification=notification, user=user)
    assert notification.read_at is not None
    assert mark_all_as_read(user=other) == 1
    assert soft_delete(notification=notification, user=other) is False
    assert soft_delete(notification=notification, user=user) is True
    assert Notification.objects.active().filter(pk=notification.pk).exists() is False
    clear_all(user=other)
    assert Notification.objects.active().filter(pk=other_notification.pk).exists() is False


@pytest.mark.django_db
def test_create_notification_defers_push_and_email_until_commit():
    user = UserFactory()
    with patch('notifications.services.push_notification') as push, patch(
        'notifications.services.send_email_notification'
    ) as email, patch('notifications.services.transaction.on_commit') as on_commit:
        notification = create_notification(user=user, notification_type='test', title='Title', body='Body')
        assert on_commit.call_count == 2
        push_callback = on_commit.call_args_list[0].args[0]
        email_callback = on_commit.call_args_list[1].args[0]
        push_callback()
        email_callback()
        push.assert_called_once_with(notification)
        email.assert_called_once_with(notification)
        push.assert_called_once_with(notification)
        email.assert_called_once_with(notification)


@pytest.mark.django_db
def test_notification_message_reports_read_state():
    notification = NotificationFactory(read_at=timezone.now())
    assert notification.is_read is True


def test_notification_consumer_requires_authentication_and_forwards_events():
    consumer = NotificationConsumer()
    consumer.scope = {'user': AnonymousUser()}
    consumer.close = AsyncMock()
    async_to_sync(consumer.connect)()
    consumer.close.assert_awaited_once()

    consumer = NotificationConsumer()
    consumer.scope = {'user': UserFactory.build(id=42, username='socket-user')}
    consumer.channel_name = 'channel-1'
    consumer.channel_layer = Mock()
    consumer.channel_layer.group_add = AsyncMock()
    consumer.accept = AsyncMock()
    async_to_sync(consumer.connect)()
    consumer.channel_layer.group_add.assert_awaited_once_with('user_42_notifications', 'channel-1')
    consumer.send = AsyncMock()
    async_to_sync(consumer.notification_created)({'notification': {'id': 'n1'}})
    consumer.send.assert_awaited_once()
