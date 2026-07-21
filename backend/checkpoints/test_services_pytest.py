import pytest
from rest_framework.exceptions import ValidationError

from checkpoints.models import CheckpointQRCodeScan
from checkpoints.services import QRCodeAlreadyScanned, create_checkpoint_qr_code, scan_checkpoint_qr_code
from tests.factories import CheckpointFactory, ParticipantFactory, UserFactory


@pytest.mark.django_db
def test_qr_scan_awards_points_and_is_idempotently_rejected():
    checkpoint = CheckpointFactory()
    creator = checkpoint.created_by
    participant = ParticipantFactory(activity=checkpoint.activity)
    qr_code = create_checkpoint_qr_code(
        checkpoint=checkpoint, created_by=creator, points=7
    )

    scan_checkpoint_qr_code(
        user=participant.user, token=qr_code.qr_token,
        latitude=checkpoint.latitude, longitude=checkpoint.longitude,
    )
    with pytest.raises(QRCodeAlreadyScanned):
        scan_checkpoint_qr_code(
            user=participant.user, token=qr_code.qr_token,
            latitude=checkpoint.latitude, longitude=checkpoint.longitude,
        )

    assert CheckpointQRCodeScan.objects.filter(qr_code=qr_code).count() == 1
    assert participant.user.room_points.get(room=checkpoint.activity).points == 7


@pytest.mark.django_db
def test_qr_scan_rejects_unknown_token_and_outside_radius():
    checkpoint = CheckpointFactory(radius=1)
    participant = ParticipantFactory(activity=checkpoint.activity)
    qr_code = create_checkpoint_qr_code(checkpoint=checkpoint, created_by=UserFactory())

    with pytest.raises(ValidationError, match='QR code not found'):
        scan_checkpoint_qr_code(
            user=participant.user, token='00000000-0000-0000-0000-000000000000',
            latitude=checkpoint.latitude, longitude=checkpoint.longitude,
        )
    with pytest.raises(ValidationError, match='outside the checkpoint radius'):
        scan_checkpoint_qr_code(
            user=participant.user, token=qr_code.qr_token,
            latitude=checkpoint.latitude + 1, longitude=checkpoint.longitude,
        )
