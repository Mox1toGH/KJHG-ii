import json
from unittest.mock import AsyncMock

from asgiref.sync import async_to_sync
from django.contrib.auth.models import AnonymousUser

from tracking.consumers import TrackingConsumer


def test_tracking_consumer_rejects_anonymous_connections():
    consumer = TrackingConsumer()
    consumer.scope = {
        'user': AnonymousUser(),
        'url_route': {'kwargs': {'activity_id': 'activity-id'}},
    }
    consumer.close = AsyncMock()

    async_to_sync(consumer.connect)()

    consumer.close.assert_awaited_once()


def test_tracking_consumer_ignores_malformed_and_incomplete_updates():
    consumer = TrackingConsumer()
    consumer.activity_id = 'activity-id'
    consumer.handle_location_update = AsyncMock()

    async_to_sync(consumer.receive)('{not-json')
    async_to_sync(consumer.receive)(json.dumps({'type': 'location.update'}))

    consumer.handle_location_update.assert_awaited_once_with({'type': 'location.update'})
