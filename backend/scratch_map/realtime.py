import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .serializers import ScratchDiscoverySerializer

logger = logging.getLogger(__name__)


def scratch_map_group_name(user_id: int) -> str:
    return f'scratch_map.user.{user_id}'


def _publish(user_id: int, event: str, payload: dict) -> None:
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    async_to_sync(channel_layer.group_send)(
        scratch_map_group_name(user_id),
        {
            'type': 'scratch_map_event',
            'event': event,
            'payload': payload,
        },
    )
    logger.info('Published Scratch Map event %s for user %s', event, user_id)


def publish_cell_discovered(discovery) -> None:
    _publish(
        discovery.user_id,
        'scratch_map.cell_discovered',
        {'discovery': ScratchDiscoverySerializer(discovery).data},
    )


def publish_statistics_updated(user_id: int, statistics: dict) -> None:
    _publish(user_id, 'scratch_map.statistics_updated', {'statistics': statistics})
