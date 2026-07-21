from io import BytesIO
from math import atan2, cos, radians, sin, sqrt

import qrcode
from django.core.files.base import ContentFile
from django.db import IntegrityError, transaction
from django.db.models import F
from rest_framework.exceptions import APIException, ValidationError
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from .models import Checkpoint, CheckpointQRCode, CheckpointQRCodeScan
from .selectors import get_checkpoint_qr_code_for_update, get_participant_for_user
from points.models import Point


class QRCodeAlreadyScanned(APIException):
    status_code = 409
    default_detail = 'This QR code has already been scanned.'
    default_code = 'qr_code_already_scanned'


def calculate_distance(lat1, lon1, lat2, lon2) -> float:
    earth_radius = 6371000
    phi1, phi2 = radians(lat1), radians(lat2)
    delta_phi = radians(lat2 - lat1)
    delta_lambda = radians(lon2 - lon1)
    a = sin(delta_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(delta_lambda / 2) ** 2
    return earth_radius * 2 * atan2(sqrt(a), sqrt(1 - a))


def _qr_png(token) -> bytes:
    image = qrcode.make(str(token))
    output = BytesIO()
    image.save(output, format='PNG')
    return output.getvalue()


@transaction.atomic
def create_checkpoint_qr_code(*, checkpoint: Checkpoint, created_by, name: str | None = None, points: int = 0):
    if not name:
        name = f'QR {checkpoint.qr_codes.count() + 1}'
    qr_code = CheckpointQRCode.objects.create(checkpoint=checkpoint, name=name, created_by=created_by, points=points)
    qr_code.image.save(f'{qr_code.id}.png', ContentFile(_qr_png(qr_code.qr_token)), save=True)
    return qr_code


def delete_checkpoint_qr_code(*, qr_code: CheckpointQRCode):
    qr_code.delete()


@transaction.atomic
def scan_checkpoint_qr_code(*, user, token, latitude: float, longitude: float):
    try:
        qr_code = get_checkpoint_qr_code_for_update(token=token)
    except CheckpointQRCode.DoesNotExist:
        raise ValidationError({'token': 'QR code not found.'})

    participant = get_participant_for_user(user=user, activity_id=qr_code.checkpoint.activity_id)
    if participant is None:
        raise ValidationError({'detail': 'You do not belong to this activity.'})
    if qr_code.created_by_id == user.id:
        raise ValidationError({'detail': 'You cannot scan a QR code you created.'})
    if CheckpointQRCodeScan.objects.filter(qr_code=qr_code, participant=participant).exists():
        raise QRCodeAlreadyScanned()

    distance = calculate_distance(
        latitude, longitude, qr_code.checkpoint.latitude, qr_code.checkpoint.longitude
    )
    if distance > qr_code.checkpoint.radius:
        raise ValidationError({'detail': 'You are outside the checkpoint radius.'})

    try:
        scan = CheckpointQRCodeScan.objects.create(qr_code=qr_code, participant=participant)
    except IntegrityError:
        raise QRCodeAlreadyScanned()

    # Award points for scanning QR code
    if qr_code.points > 0:
        activity = qr_code.checkpoint.activity
        user_point, pt_created = Point.objects.get_or_create(
            user=user,
            room=activity,
            defaults={'points': qr_code.points},
        )
        if not pt_created:
            Point.objects.filter(pk=user_point.pk).update(points=F('points') + qr_code.points)
            user_point.refresh_from_db()

    return scan


def build_qr_codes_pdf(*, checkpoint: Checkpoint, qr_codes):
    output = BytesIO()
    pdf = canvas.Canvas(output, pagesize=A4)
    page_width, page_height = A4
    for qr_code in qr_codes:
        pdf.setFont('Helvetica-Bold', 18)
        pdf.drawCentredString(page_width / 2, page_height - 90, checkpoint.name)
        pdf.setFont('Helvetica', 16)
        pdf.drawCentredString(page_width / 2, page_height - 120, qr_code.name)
        with qr_code.image.open('rb') as image_file:
            image = ImageReader(image_file)
            size = min(page_width, page_height) * 0.55
            pdf.drawImage(
                image, (page_width - size) / 2, (page_height - size) / 2,
                width=size, height=size, preserveAspectRatio=True, mask='auto'
            )
        pdf.showPage()
    pdf.save()
    output.seek(0)
    return output
