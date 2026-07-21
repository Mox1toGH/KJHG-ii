from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction


def activity_chat_group(activity_id):
    return f'activity_{activity_id}_chat'


def chat_message_payload(message):
    sender = message.sender
    current_status = sender.current_status.name if sender.current_status_id else None
    return {
        'id': str(message.id),
        'activity': str(message.activity_id),
        'sender': {
            'id': sender.id,
            'username': sender.username,
            'email': sender.email,
            'first_name': sender.first_name,
            'last_name': sender.last_name,
            'avatar': sender.avatar.url if sender.avatar else None,
            'current_status': current_status,
            'created_at': sender.date_joined.isoformat().replace('+00:00', 'Z'),
            'last_seen': sender.last_login.isoformat().replace('+00:00', 'Z') if sender.last_login else None,
        },
        'body': message.body,
        'created_at': message.created_at.isoformat().replace('+00:00', 'Z'),
    }


def publish_chat_message(message):
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    async_to_sync(channel_layer.group_send)(
        activity_chat_group(message.activity_id),
        {'type': 'chat.message_created', 'message': chat_message_payload(message)},
    )


def create_chat_message(*, activity, sender, body):
    message = activity.chat_messages.create(sender=sender, body=body)
    transaction.on_commit(lambda: publish_chat_message(message))
    return message
