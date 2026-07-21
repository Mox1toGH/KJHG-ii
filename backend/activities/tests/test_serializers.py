import pytest

from activities.models import ActivityRole, PermissionCode
from activities.serializers import ActivityRoleSerializer, ActivitySerializer, ParticipantSerializer
from tests.factories import ActivityFactory, ActivityRoleFactory, ParticipantFactory


@pytest.mark.django_db
def test_activity_role_serializer_rejects_unknown_permission():
    serializer = ActivityRoleSerializer(data={'name': 'Mapper', 'permissions': [{'code': 'not-real'}]})
    assert serializer.is_valid() is False
    assert 'Unknown permission' in str(serializer.errors)


@pytest.mark.django_db
def test_activity_role_serializer_rejects_invalid_map_scope():
    serializer = ActivityRoleSerializer(data={
        'name': 'Mapper',
        'permissions': [{'code': PermissionCode.VIEW_PARTICIPANTS_MAP, 'scope': {'visibility': 'invalid'}}],
    })
    assert serializer.is_valid() is False
    assert 'Map visibility' in str(serializer.errors)


@pytest.mark.django_db
def test_participant_serializer_rejects_role_from_another_activity():
    participant = ParticipantFactory()
    foreign_role = ActivityRoleFactory()
    serializer = ParticipantSerializer(
        participant,
        data={'role_id': str(foreign_role.id)},
        partial=True,
        context={'activity': participant.activity},
    )
    assert serializer.is_valid() is False
    assert 'Role must belong' in str(serializer.errors)


@pytest.mark.django_db
def test_activity_serializer_rejects_owner_as_default_role():
    activity = ActivityFactory()
    owner_role = ActivityRole.objects.create(activity=activity, name='Owner')
    serializer = ActivitySerializer(activity, data={'default_role_id': str(owner_role.id)}, partial=True)
    assert serializer.is_valid() is False
    assert 'Owner role' in str(serializer.errors)
