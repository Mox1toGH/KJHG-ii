import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.exceptions import ValidationError
from django.db import OperationalError
from channels.db import database_sync_to_async
from activities.models import Participant
from activities.permissions import participant_map_scope
from .services import update_participant_location, activity_tracking_group

logger = logging.getLogger(__name__)

class TrackingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.activity_id = self.scope['url_route']['kwargs']['activity_id']
        self.room_group_name = activity_tracking_group(self.activity_id)
        
        # Check authentication
        if not self.scope['user'].is_authenticated:
            await self.close()
            return
            
        # Verify user is a participant
        self.participant = await self.get_participant()
        if not self.participant:
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
        except (TypeError, json.JSONDecodeError):
            logger.warning('Invalid tracking message for activity %s', self.activity_id)
            return
        event_type = text_data_json.get('type')

        if event_type == 'location.update':
            await self.handle_location_update(text_data_json)
        # Future events like 'status.update', 'sos.alert' can be handled here

    async def handle_location_update(self, data):
        try:
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            
            if latitude is None or longitude is None:
                return

            location = await self.update_location_db(
                latitude=latitude,
                longitude=longitude,
                accuracy=data.get('accuracy'),
                heading=data.get('heading'),
                speed=data.get('speed')
            )

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'location.updated',
                    'participant_id': str(self.participant.id),
                    'participant': {
                        'user': {
                            'id': str(self.participant.user.id),
                            'username': self.participant.user.username,
                            'display_name': ' '.join(filter(None, [
                                self.participant.user.first_name,
                                self.participant.user.last_name,
                            ])),
                        },
                        'role': {
                            'id': str(self.participant.role.id),
                            'name': self.participant.role.name,
                        } if self.participant.role else None,
                    },
                    'location': {
                        'latitude': float(location.latitude),
                        'longitude': float(location.longitude),
                        'accuracy': location.accuracy,
                        'heading': location.heading,
                        'speed': location.speed,
                    },
                    'updated_at': location.updated_at.isoformat().replace('+00:00', 'Z')
                }
            )
        except (ValidationError, TypeError, ValueError, OperationalError) as error:
            logger.warning('Rejected location update for activity %s: %s', self.activity_id, error)

    async def location_updated(self, event):
        if not await self.can_view_participant(event['participant_id']):
            return
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'event': 'location.updated',
            'participant_id': event['participant_id'],
            'participant': event['participant'],
            'location': event['location'],
            'updated_at': event['updated_at']
        }))

    async def sos_updated(self, event):
        # The activator receives the API response; every other activity member
        # receives the WebSocket event immediately.
        if str(self.scope['user'].id) == str(event.get('exclude_user_id')):
            return
        await self.send(text_data=json.dumps({'event': 'sos.updated', 'sos': event['sos']}))

    @database_sync_to_async
    def can_view_participant(self, participant_id):
        if str(self.participant.id) == str(participant_id):
            return True
        visible_role_ids = participant_map_scope(
            user=self.scope['user'], activity=self.participant.activity
        )
        return visible_role_ids is None or str(self.get_participant_role_id(participant_id)) in {
            str(role_id) for role_id in visible_role_ids
        }

    def get_participant_role_id(self, participant_id):
        return Participant.objects.filter(pk=participant_id).values_list('role_id', flat=True).first()

    @database_sync_to_async
    def get_participant(self):
        try:
            return Participant.objects.select_related('user', 'role').get(
                activity_id=self.activity_id,
                user=self.scope['user']
            )
        except Participant.DoesNotExist:
            return None

    @database_sync_to_async
    def update_location_db(self, latitude, longitude, accuracy, heading, speed):
        return update_participant_location(
            self.participant,
            latitude,
            longitude,
            accuracy,
            heading,
            speed
        )
