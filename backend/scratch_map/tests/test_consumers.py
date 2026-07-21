from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from asgiref.sync import async_to_sync
from django.contrib.auth.models import AnonymousUser
from django.test import SimpleTestCase

from scratch_map.consumers import ScratchMapConsumer
from scratch_map.realtime import scratch_map_group_name


class ScratchMapConsumerTests(SimpleTestCase):
    def test_unauthenticated_connection_is_rejected(self):
        consumer = ScratchMapConsumer()
        consumer.scope = {'user': AnonymousUser()}
        consumer.close = AsyncMock()

        async_to_sync(consumer.connect)()

        consumer.close.assert_awaited_once_with(code=4401)

    def test_authenticated_connection_joins_private_group(self):
        consumer = ScratchMapConsumer()
        consumer.scope = {'user': SimpleNamespace(id=42, is_authenticated=True)}
        consumer.channel_name = 'channel-1'
        consumer.channel_layer = Mock()
        consumer.channel_layer.group_add = AsyncMock()
        consumer.accept = AsyncMock()

        async_to_sync(consumer.connect)()

        consumer.channel_layer.group_add.assert_awaited_once_with(
            scratch_map_group_name(42),
            'channel-1',
        )
        consumer.accept.assert_awaited_once()

    def test_event_is_delivered_without_consumer_business_logic(self):
        consumer = ScratchMapConsumer()
        consumer.send_json = AsyncMock()

        async_to_sync(consumer.scratch_map_event)(
            {
                'event': 'scratch_map.cell_discovered',
                'payload': {'discovery': {'h3_index': 'cell'}},
            }
        )

        consumer.send_json.assert_awaited_once_with(
            {
                'event': 'scratch_map.cell_discovered',
                'payload': {'discovery': {'h3_index': 'cell'}},
            }
        )
