import pytest
from rest_framework import status

from points.models import Point
from tests.factories import ActivityFactory, ParticipantFactory, PointFactory, UserFactory


@pytest.mark.django_db
def test_points_endpoint_returns_only_accessible_rooms(api_client):
    owner = UserFactory()
    activity = ActivityFactory(created_by=owner)
    member = ParticipantFactory(activity=activity).user
    other_activity = ActivityFactory()
    PointFactory(room=activity, user=member, points=42)
    PointFactory(room=other_activity)
    api_client.force_authenticate(member)

    response = api_client.get('/api/points/', {'room_id': str(activity.pk)})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['points'] == 42


@pytest.mark.django_db
def test_points_serializer_uses_full_name_then_username(api_client):
    owner = UserFactory(first_name='Ada', last_name='Lovelace')
    activity = ActivityFactory(created_by=owner)
    PointFactory(room=activity, user=owner)
    api_client.force_authenticate(owner)

    response = api_client.get('/api/points/')

    assert response.data[0]['display_name'] == 'Ada Lovelace'
