from rest_framework import permissions
from .models import Participant, PermissionCode


def get_activity_for_object(obj):
    return obj.activity if hasattr(obj, 'activity') else obj


def is_activity_owner(*, user, activity):
    return activity.created_by_id == user.id


def get_participant(*, user, activity):
    return Participant.objects.select_related('role').filter(
        activity=activity, user=user
    ).first()


def has_activity_permission(*, user, activity, permission_code):
    if not user or not user.is_authenticated:
        return False
    if is_activity_owner(user=user, activity=activity):
        return True
    participant = get_participant(user=user, activity=activity)
    return bool(participant and participant.role and participant.role.permission_grants.filter(
        permission__code=permission_code
    ).exists())


def participant_map_scope(*, user, activity):
    """Return the role ids visible to this user, or None for all roles."""
    if is_activity_owner(user=user, activity=activity):
        return None
    participant = get_participant(user=user, activity=activity)
    if not participant or not participant.role:
        return set()
    grant = participant.role.permission_grants.select_related('permission').filter(
        permission__code=PermissionCode.VIEW_PARTICIPANTS_MAP
    ).first()
    if not grant:
        return set()
    if grant.scope.get('visibility', 'everyone') == 'everyone':
        return None
    return set(grant.scope.get('role_ids', []))

class IsActivityParticipant(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        activity = get_activity_for_object(obj)
        return is_activity_owner(user=request.user, activity=activity) or Participant.objects.filter(
            activity=activity, user=request.user
        ).exists()

class IsActivityOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return is_activity_owner(user=request.user, activity=get_activity_for_object(obj))


class HasActivityPermission(permissions.BasePermission):
    permission_code = None

    def has_object_permission(self, request, view, obj):
        return has_activity_permission(
            user=request.user,
            activity=get_activity_for_object(obj),
            permission_code=self.permission_code,
        )
