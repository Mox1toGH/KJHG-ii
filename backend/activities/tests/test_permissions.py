import pytest

from activities.models import ActivityPermission, ActivityRole, RolePermission
from activities.permissions import (
    has_activity_permission,
    participant_map_scope,
)
from tests.factories import ActivityFactory, ParticipantFactory, UserFactory


@pytest.mark.django_db
def test_activity_owner_has_all_permissions_and_anonymous_has_none():
    owner = UserFactory()
    activity = ActivityFactory(created_by=owner)
    permission = ActivityPermission.objects.first()
    assert has_activity_permission(user=owner, activity=activity, permission_code=permission.code)
    assert has_activity_permission(user=None, activity=activity, permission_code=permission.code) is False


@pytest.mark.django_db
def test_participant_map_scope_supports_everyone_and_role_visibility():
    owner = UserFactory()
    activity = ActivityFactory(created_by=owner)
    role = ActivityRole.objects.create(activity=activity, name='Mapper')
    participant = ParticipantFactory(activity=activity, role=role)
    permission = ActivityPermission.objects.get(code='participants.map.view')
    grant = RolePermission.objects.create(role=role, permission=permission, scope={'visibility': 'everyone'})
    assert participant_map_scope(user=participant.user, activity=activity) is None
    grant.scope = {'visibility': 'roles', 'role_ids': [str(role.id)]}
    grant.save(update_fields=['scope'])
    assert participant_map_scope(user=participant.user, activity=activity) == {str(role.id)}
