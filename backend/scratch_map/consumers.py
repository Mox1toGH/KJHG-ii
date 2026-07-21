import logging

from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .realtime import scratch_map_group_name

logger = logging.getLogger(__name__)


class ScratchMapConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            logger.warning('Rejected unauthenticated Scratch Map WebSocket connection')
            await self.close(code=4401)
            return

        self.group_name = scratch_map_group_name(user.id)
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info('Scratch Map WebSocket connected for user %s', user.id)

    async def disconnect(self, code):
        group_name = getattr(self, 'group_name', None)
        if group_name:
            await self.channel_layer.group_discard(group_name, self.channel_name)
        logger.info('Scratch Map WebSocket disconnected')

    async def scratch_map_event(self, event):
        await self.send_json({'event': event['event'], 'payload': event['payload']})
