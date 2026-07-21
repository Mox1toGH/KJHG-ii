import json
from unittest.mock import AsyncMock, Mock, patch

import pytest
from asgiref.sync import async_to_sync
from django.contrib.auth.models import AnonymousUser
from rest_framework import status

from chat.consumers import ChatConsumer
from chat.models import ChatMessage
from chat.services import activity_chat_group, create_chat_message
from tests.factories import ActivityFactory, ChatMessageFactory, ParticipantFactory, UserFactory


@pytest.mark.django_db
def test_chat_messages_are_scoped_to_activity_and_participants(api_client):
    activity = ActivityFactory()
    member = ParticipantFactory(activity=activity).user
    outsider = UserFactory()
    ChatMessageFactory(activity=activity, sender=member, body='hello')
    ChatMessageFactory(sender=outsider, body='private')
    api_client.force_authenticate(member)

    response = api_client.get(f'/api/chat/activities/{activity.pk}/messages/')

    assert response.status_code == status.HTTP_200_OK
    assert [item['body'] for item in response.data] == ['hello']


@pytest.mark.django_db
def test_chat_create_trims_body_and_publishes_after_commit(api_client, django_capture_on_commit_callbacks):
    activity = ActivityFactory()
    member = ParticipantFactory(activity=activity).user
    api_client.force_authenticate(member)

    with patch('chat.services.publish_chat_message') as publish, django_capture_on_commit_callbacks(execute=True):
        response = api_client.post(
            f'/api/chat/activities/{activity.pk}/messages/', {'body': '  hello  '}, format='json'
        )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['body'] == 'hello'
    assert ChatMessage.objects.get().body == 'hello'
    publish.assert_called_once()


@pytest.mark.django_db
def test_chat_rejects_empty_and_forbids_non_members(api_client):
    activity = ActivityFactory()
    outsider = UserFactory()
    api_client.force_authenticate(outsider)

    response = api_client.post(
        f'/api/chat/activities/{activity.pk}/messages/', {'body': 'hello'}, format='json'
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    member = ParticipantFactory(activity=activity).user
    api_client.force_authenticate(member)
    response = api_client.post(
        f'/api/chat/activities/{activity.pk}/messages/', {'body': '   '}, format='json'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_chat_consumer_rejects_anonymous_and_invalid_messages():
    consumer = ChatConsumer()
    consumer.scope = {'user': AnonymousUser(), 'url_route': {'kwargs': {'activity_id': 'x'}}}
    consumer.close = AsyncMock()
    async_to_sync(consumer.connect)()
    consumer.close.assert_awaited_once()

    consumer = ChatConsumer()
    consumer.activity_id = 'x'
    consumer.send = AsyncMock()
    async_to_sync(consumer.handle_message_create)({'body': ' '})
    consumer.send.assert_awaited_once_with(
        text_data=json.dumps({'event': 'chat.error', 'detail': 'Message cannot be empty.'})
    )


@pytest.mark.django_db
def test_create_chat_message_uses_expected_group_name(django_capture_on_commit_callbacks):
    activity = ActivityFactory()
    sender = ParticipantFactory(activity=activity).user
    with patch('chat.services.publish_chat_message') as publish, django_capture_on_commit_callbacks(execute=True):
        message = create_chat_message(activity=activity, sender=sender, body='hello')
    assert activity_chat_group(activity.pk) == f'activity_{activity.pk}_chat'
    publish.assert_called_once_with(message)
