import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from activities.models import Activity, Participant

User = get_user_model()

class Checkpoint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='checkpoints', verbose_name=_('Activity'))
    name = models.CharField(max_length=200, verbose_name=_('Name'))
    points = models.IntegerField(default=0, verbose_name=_('Points'))
    description = models.TextField(blank=True, default='', verbose_name=_('Description'))
    color = models.CharField(max_length=20, default='#9333EA', verbose_name=_('Color'))
    latitude = models.FloatField(verbose_name=_('Latitude'))
    longitude = models.FloatField(verbose_name=_('Longitude'))
    radius = models.FloatField(default=50.0, verbose_name=_('Radius'))
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_checkpoints', verbose_name=_('Created by'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Checkpoint')
        verbose_name_plural = _('Checkpoints')

    def __str__(self):
        return f"Checkpoint {self.name} in {self.activity.title}"


class CheckpointQRCode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    checkpoint = models.ForeignKey(Checkpoint, on_delete=models.CASCADE, related_name='qr_codes', verbose_name=_('Checkpoint'))
    name = models.CharField(max_length=200, verbose_name=_('Name'))
    qr_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, verbose_name=_('QR token'))
    image = models.ImageField(upload_to='checkpoint_qrcodes/%Y/%m/', verbose_name=_('Image'))
    points = models.IntegerField(default=0, verbose_name=_('Points'))
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_checkpoint_qr_codes', verbose_name=_('Created by'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = _('Checkpoint QR Code')
        verbose_name_plural = _('Checkpoint QR Codes')

    def __str__(self):
        return f"{self.name} for {self.checkpoint.name}"


class CheckpointQRCodeScan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qr_code = models.ForeignKey(CheckpointQRCode, on_delete=models.CASCADE, related_name='scans', verbose_name=_('QR code'))
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='checkpoint_qr_scans', verbose_name=_('Participant'))
    scanned_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Scanned at'))

    class Meta:
        ordering = ['-scanned_at']
        verbose_name = _('Checkpoint QR Code Scan')
        verbose_name_plural = _('Checkpoint QR Code Scans')
        constraints = [
            models.UniqueConstraint(fields=['qr_code', 'participant'], name='unique_qr_code_participant_scan'),
        ]


class Route(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='routes', verbose_name=_('Activity'))
    name = models.CharField(max_length=200, verbose_name=_('Name'))
    description = models.TextField(blank=True, default='', verbose_name=_('Description'))
    color = models.CharField(max_length=20, default='#8B5CF6', verbose_name=_('Color'))
    main_checkpoint = models.OneToOneField(Checkpoint, on_delete=models.CASCADE, related_name='route', verbose_name=_('Main checkpoint'))
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_routes', verbose_name=_('Created by'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Route')
        verbose_name_plural = _('Routes')

    def __str__(self):
        return f"Route {self.name} in {self.activity.title}"


class RoutePoint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='points', verbose_name=_('Route'))
    sequence_number = models.PositiveIntegerField(verbose_name=_('Sequence number'))
    name = models.CharField(max_length=200, blank=True, default='', verbose_name=_('Name'))
    points = models.IntegerField(default=0, verbose_name=_('Points'))
    description = models.TextField(blank=True, default='', verbose_name=_('Description'))
    latitude = models.FloatField(verbose_name=_('Latitude'))
    longitude = models.FloatField(verbose_name=_('Longitude'))
    radius = models.FloatField(default=50.0, verbose_name=_('Radius'))

    class Meta:
        ordering = ['sequence_number']
        verbose_name = _('Route Point')
        verbose_name_plural = _('Route Points')
        unique_together = ('route', 'sequence_number')

    def __str__(self):
        return f"RoutePoint {self.sequence_number} for {self.route.name}"


class Visit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='checkpoint_visits', verbose_name=_('Participant'))
    checkpoint = models.ForeignKey(Checkpoint, on_delete=models.CASCADE, null=True, blank=True, related_name='visits', verbose_name=_('Checkpoint'))
    route_point = models.ForeignKey(RoutePoint, on_delete=models.CASCADE, null=True, blank=True, related_name='visits', verbose_name=_('Route point'))
    visited_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Visited at'))
    is_manual = models.BooleanField(default=False, verbose_name=_('Is manual'))
    deviation = models.FloatField(null=True, blank=True, verbose_name=_('Deviation'))

    class Meta:
        ordering = ['-visited_at']
        verbose_name = _('Visit')
        verbose_name_plural = _('Visits')
        constraints = [
            models.CheckConstraint(
                condition=models.Q(checkpoint__isnull=False, route_point__isnull=True) |
                          models.Q(checkpoint__isnull=True, route_point__isnull=False),
                name='visit_has_exactly_one_point'
            )
        ]

    def __str__(self):
        return f"Visit by {self.participant.user.username}"


class CheckpointPhoto(models.Model):
    checkpoint = models.ForeignKey(Checkpoint, on_delete=models.CASCADE, related_name='photos', verbose_name=_('Checkpoint'))
    image = models.ImageField(upload_to='checkpoints/%Y/%m/', verbose_name=_('Image'))
    is_main = models.BooleanField(default=False, verbose_name=_('Is main'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Checkpoint Photo')
        verbose_name_plural = _('Checkpoint Photos')

    def save(self, *args, **kwargs):
        if not self.pk and not self.checkpoint.photos.exists():
            self.is_main = True
        super().save(*args, **kwargs)
        if self.is_main:
            type(self).objects.filter(checkpoint=self.checkpoint).exclude(pk=self.pk).update(is_main=False)

    def delete(self, *args, **kwargs):
        checkpoint = self.checkpoint
        was_main = self.is_main
        result = super().delete(*args, **kwargs)
        if was_main:
            next_photo = checkpoint.photos.order_by('created_at').first()
            if next_photo:
                next_photo.is_main = True
                next_photo.save(update_fields=['is_main'])
        return result


class RoutePointPhoto(models.Model):
    route_point = models.ForeignKey(RoutePoint, on_delete=models.CASCADE, related_name='photos', verbose_name=_('Route point'))
    image = models.ImageField(upload_to='route_points/%Y/%m/', verbose_name=_('Image'))
    is_main = models.BooleanField(default=False, verbose_name=_('Is main'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Route Point Photo')
        verbose_name_plural = _('Route Point Photos')

    def save(self, *args, **kwargs):
        if not self.pk and not self.route_point.photos.exists():
            self.is_main = True
        super().save(*args, **kwargs)
        if self.is_main:
            type(self).objects.filter(route_point=self.route_point).exclude(pk=self.pk).update(is_main=False)

    def delete(self, *args, **kwargs):
        route_point = self.route_point
        was_main = self.is_main
        result = super().delete(*args, **kwargs)
        if was_main:
            next_photo = route_point.photos.order_by('created_at').first()
            if next_photo:
                next_photo.is_main = True
                next_photo.save(update_fields=['is_main'])
        return result
