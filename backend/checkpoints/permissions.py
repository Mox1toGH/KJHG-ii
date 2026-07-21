from rest_framework import permissions

from activities.models import PermissionCode
from activities.permissions import has_activity_permission, is_activity_owner


def is_checkpoint_qr_manager(*, user, checkpoint) -> bool:
    return bool(
        user and user.is_authenticated and (
            checkpoint.created_by_id == user.id
            or is_activity_owner(user=user, activity=checkpoint.activity)
        ) and has_activity_permission(
            user=user,
            activity=checkpoint.activity,
            permission_code=PermissionCode.MANAGE_CHECKPOINT_QRCODES,
        )
    )


class IsCheckpointQRCodeManager(permissions.BasePermission):
    message = 'Only the checkpoint creator or Activity Owner can manage QR codes.'

    def has_object_permission(self, request, view, obj):
        checkpoint = getattr(obj, 'checkpoint', obj)
        return is_checkpoint_qr_manager(user=request.user, checkpoint=checkpoint)
