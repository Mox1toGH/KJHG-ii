from django.db.models import QuerySet

from activities.models import Participant

from .models import Checkpoint, CheckpointQRCode


def get_checkpoint_queryset():
    return Checkpoint.objects.select_related('activity', 'created_by')


def get_checkpoint(*, checkpoint_id) -> Checkpoint:
    return get_checkpoint_queryset().get(pk=checkpoint_id)


def get_checkpoint_qr_codes(*, checkpoint: Checkpoint) -> QuerySet[CheckpointQRCode]:
    return CheckpointQRCode.objects.filter(checkpoint=checkpoint).select_related('checkpoint', 'created_by')


def get_checkpoint_qr_code(*, qr_code_id) -> CheckpointQRCode:
    return get_checkpoint_qr_code_queryset().get(pk=qr_code_id)


def get_checkpoint_qr_code_queryset():
    return CheckpointQRCode.objects.select_related('checkpoint__activity', 'created_by')


def get_checkpoint_qr_code_for_update(*, token) -> CheckpointQRCode:
    return CheckpointQRCode.objects.select_for_update().select_related(
        'checkpoint__activity', 'created_by'
    ).get(qr_token=token)


def get_participant_for_user(*, user, activity_id):
    return Participant.objects.filter(user=user, activity_id=activity_id).first()


def get_checkpoint_qr_progress(*, checkpoint: Checkpoint, user) -> dict[str, int]:
    total = checkpoint.qr_codes.count()
    participant = get_participant_for_user(user=user, activity_id=checkpoint.activity_id)
    scanned = checkpoint.qr_codes.filter(scans__participant=participant).count() if participant else 0
    return {'scanned': scanned, 'total': total}
