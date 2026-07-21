from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from scratch_map.realtime import publish_cell_discovered, scratch_map_group_name


class ScratchMapRealtimeTests(SimpleTestCase):
    @patch('scratch_map.realtime.async_to_sync')
    @patch('scratch_map.realtime.get_channel_layer')
    def test_cell_event_uses_private_user_group(self, get_layer, async_to_sync):
        layer = Mock()
        get_layer.return_value = layer
        sender = Mock()
        async_to_sync.return_value = sender
        discovery = Mock(user_id=42)
        discovery.id = 'discovery-id'
        discovery.h3_index = 'cell'
        discovery.discovered_at = None

        with patch('scratch_map.realtime.ScratchDiscoverySerializer') as serializer:
            serializer.return_value.data = {'h3_index': 'cell'}
            publish_cell_discovered(discovery)

        sender.assert_called_once_with(
            scratch_map_group_name(42),
            {
                'type': 'scratch_map_event',
                'event': 'scratch_map.cell_discovered',
                'payload': {'discovery': {'h3_index': 'cell'}},
            },
        )
