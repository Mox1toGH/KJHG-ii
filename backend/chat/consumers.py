import json
import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.exceptions import ValidationError
from django.db import OperationalError

from activities.models import Activity
from activities.models import Participant
from activities.permissions import is_activity_owner
from .services import activity_chat_group, create_chat_message

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.activity_id = self.scope['url_route']['kwargs']['activity_id']
        self.group_name = activity_chat_group(self.activity_id)

        if not self.scope['user'].is_authenticated:
            await self.close()
            return

        if not await self.can_access_activity():
            await self.close()
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            payload = json.loads(text_data)
        except (TypeError, json.JSONDecodeError):
            logger.warning('Invalid chat message for activity %s', self.activity_id)
            return

        if payload.get('type') == 'chat.message.create':
            await self.handle_message_create(payload)

    async def handle_message_create(self, payload):
        body = str(payload.get('body', '')).strip()
        if not body:
            await self.send_error('Message cannot be empty.')
            return
        if len(body) > 2000:
            await self.send_error('Message is too long.')
            return

        try:
            await self.create_message(body)
        except (ValidationError, OperationalError, ValueError) as error:
            logger.warning('Rejected chat message for activity %s: %s', self.activity_id, error)
            await self.send_error('Message could not be sent.')

    async def chat_message_created(self, event):
        await self.send(text_data=json.dumps({
            'event': 'chat.message_created',
            'message': event['message'],
        }))

    async def send_error(self, detail):
        await self.send(text_data=json.dumps({
            'event': 'chat.error',
            'detail': detail,
        }))

    @database_sync_to_async
    def can_access_activity(self):
        user = self.scope['user']
        activity = Activity.objects.filter(pk=self.activity_id).first()
        if activity is None:
            return False
        return Participant.objects.filter(
            activity_id=self.activity_id,
            user=user,
        ).exists() or is_activity_owner(user=user, activity=activity)

    @database_sync_to_async
    def create_message(self, body):
        activity = Activity.objects.get(pk=self.activity_id)
        return create_chat_message(activity=activity, sender=self.scope['user'], body=body)
