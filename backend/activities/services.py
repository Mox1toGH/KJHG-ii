from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from .models import Activity, ActivityRole, ActivityPermission, Participant, PermissionCode, RolePermission, JoinRequest


OWNER_ROLE_NAME = 'Owner'
DEFAULT_PARTICIPANT_ROLE_NAME = 'User'


def is_owner_role(role: ActivityRole) -> bool:
    return role.name.casefold() == OWNER_ROLE_NAME.casefold()

def create_activity(*, user, title: str, description: str = '', status: str = Activity.Status.DRAFT, started_at=None, ended_at=None, default_role=None) -> Activity:
    with transaction.atomic():
        activity = Activity.objects.create(
            created_by=user,
            title=title,
            description=description,
            status=status,
            started_at=started_at,
            ended_at=ended_at
        )
        
        owner_role = ActivityRole.objects.create(
            activity=activity,
            name=OWNER_ROLE_NAME,
            description="Activity Owner"
        )

        default_role = ActivityRole.objects.create(
            activity=activity,
            name=DEFAULT_PARTICIPANT_ROLE_NAME,
            description="Default activity participant",
        )
        view_permission = ActivityPermission.objects.get(code=PermissionCode.VIEW_PARTICIPANTS_MAP)
        RolePermission.objects.create(
            role=default_role,
            permission=view_permission,
            scope={'visibility': 'everyone'},
        )
        activity.default_role = default_role
        activity.save(update_fields=['default_role'])
        
        Participant.objects.create(
            activity=activity,
            user=user,
            role=owner_role
        )
        
        return activity
        
def update_activity(*, activity: Activity, **data) -> Activity:
    default_role = data.get('default_role')
    if default_role is not None and default_role.activity_id != activity.id:
        raise ValidationError({'default_role_id': 'Default role must belong to this activity.'})
    if default_role is not None and is_owner_role(default_role):
        raise ValidationError({'default_role_id': 'The Owner role cannot be the default participant role.'})
    for field, value in data.items():
        if hasattr(activity, field):
            setattr(activity, field, value)
    activity.save()
    return activity

def delete_activity(*, activity: Activity):
    activity.delete()

def join_activity(*, activity: Activity, user) -> JoinRequest:
    if Participant.objects.filter(activity=activity, user=user).exists():
        raise ValidationError({"detail": "User is already a participant."})
        
    join_request, created = JoinRequest.objects.get_or_create(
        activity=activity,
        user=user,
        defaults={'status': JoinRequest.Status.PENDING}
    )
    
    if not created:
        if join_request.status == JoinRequest.Status.PENDING:
            raise ValidationError({"detail": "Запит на приєднання вже надіслано та очікує розгляду."})
        else:
            join_request.status = JoinRequest.Status.PENDING
            join_request.save()
            
    from notifications.services import create_notification
    create_notification(
        user=activity.created_by,
        notification_type='activity.join_request.created',
        title="Новий запит на приєднання",
        body=f"Користувач {user.username or user.email} хоче приєднатися до кімнати «{activity.title}»",
        data={'activity_id': str(activity.id), 'join_request_id': str(join_request.id), 'route': '/activities'}
    )
    
    return join_request


def approve_join_request(*, join_request: JoinRequest) -> Participant:
    if join_request.status != JoinRequest.Status.PENDING:
        raise ValidationError({"detail": "Запит вже оброблено."})
        
    activity = join_request.activity
    user = join_request.user
    
    if Participant.objects.filter(activity=activity, user=user).exists():
        join_request.status = JoinRequest.Status.ACCEPTED
        join_request.save()
        raise ValidationError({"detail": "Користувач вже є учасником кімнати."})
        
    with transaction.atomic():
        join_request.status = JoinRequest.Status.ACCEPTED
        join_request.save()
        
        participant = Participant(
            activity=activity,
            user=user
        )
        
        participant.role = activity.default_role or ActivityRole.objects.get(
            activity=activity, name__iexact=DEFAULT_PARTICIPANT_ROLE_NAME,
        )
        
        participant.save()
        
        from notifications.services import create_notification
        create_notification(
            user=user,
            notification_type='activity.join_request.accepted',
            title="Запит прийнято",
            body=f"Вас прийнято до кімнати «{activity.title}»",
            data={'activity_id': str(activity.id)}
        )
        
        return participant


def reject_join_request(*, join_request: JoinRequest):
    if join_request.status != JoinRequest.Status.PENDING:
        raise ValidationError({"detail": "Запит вже оброблено."})
        
    join_request.status = JoinRequest.Status.REJECTED
    join_request.save()
    
    from notifications.services import create_notification
    create_notification(
        user=join_request.user,
        notification_type='activity.join_request.rejected',
        title="Запит відхилено",
        body=f"Ваш запит на приєднання до кімнати «{join_request.activity.title}» відхилено",
        data={'activity_id': str(join_request.activity.id)}
    )


def leave_activity(*, activity: Activity, user):
    try:
        participant = Participant.objects.get(activity=activity, user=user)
    except Participant.DoesNotExist:
        raise ValidationError({"detail": "User is not a participant."})
        
    if participant.role and participant.role.name == "Owner":
        raise ValidationError({"detail": "Activity owner cannot leave until ownership is transferred."})
        
    participant.delete()


def remove_participant(*, participant: Participant):
    if participant.user_id == participant.activity.created_by_id:
        raise ValidationError({"detail": "The Activity Owner cannot be removed."})
    participant.delete()

def set_role_permissions(*, role: ActivityRole, permissions):
    """Replace grants atomically; each grant may carry a future-proof scope."""
    RolePermission.objects.filter(role=role).delete()
    for item in permissions or []:
        permission = item['permission']
        RolePermission.objects.create(role=role, permission=permission, scope=item.get('scope', {}))


def create_activity_role(*, activity: Activity, name: str, description: str = '', color: str = '', permissions=None) -> ActivityRole:
    if ActivityRole.objects.filter(activity=activity, name__iexact=name).exists():
        raise ValidationError({"detail": "Role with this name already exists in the activity."})
        
    role = ActivityRole.objects.create(
        activity=activity,
        name=name,
        description=description,
        color=color
    )
    set_role_permissions(role=role, permissions=permissions)
    return role

def update_activity_role(*, role: ActivityRole, **data) -> ActivityRole:
    permissions = data.pop('permissions', None)
    if 'name' in data and data['name'] != role.name:
        if is_owner_role(role):
            raise ValidationError({"detail": "Cannot rename the Owner role."})
        if ActivityRole.objects.filter(activity=role.activity, name__iexact=data['name']).exclude(pk=role.pk).exists():
            raise ValidationError({"detail": "Role with this name already exists in the activity."})
            
    for field, value in data.items():
        if hasattr(role, field):
            setattr(role, field, value)
    role.save()
    if permissions is not None:
        set_role_permissions(role=role, permissions=permissions)
    return role

def delete_activity_role(*, role: ActivityRole):
    if role.participants.filter(user_id=role.activity.created_by_id).exists() or is_owner_role(role):
        raise ValidationError({"detail": "The Owner role cannot be deleted."})
    role.delete()


def assign_participant_role(*, participant: Participant, role):
    if role and role.activity_id != participant.activity_id:
        raise ValidationError({'role_id': 'Role must belong to this activity.'})
    if participant.user_id == participant.activity.created_by_id:
        raise ValidationError({'detail': 'The Activity Owner cannot be reassigned.'})
    if role and is_owner_role(role):
        raise ValidationError({'detail': 'The Owner role can only belong to the activity owner.'})
    participant.role = role
    participant.save(update_fields=['role'])
    return participant
