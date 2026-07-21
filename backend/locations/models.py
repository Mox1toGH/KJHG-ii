import uuid
from django.db import models
from django.contrib.auth import get_user_model
from activities.models import Activity

User = get_user_model()

class LocationMarker(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='markers')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=20, default='#F59E0B')
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_markers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} in {self.activity.title}"


class ActivityZone(models.Model):
    class TriggerAction(models.TextChoices):
        NO_ACTION = 'no_action', 'No Action'
        ON_EXIT = 'on_exit', 'On Exit'
        ON_ENTRY = 'on_entry', 'On Entry'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='zones')
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=20, default='#10B981')
    points = models.JSONField()
    trigger_action = models.CharField(max_length=20, choices=TriggerAction.choices, default=TriggerAction.NO_ACTION)
    trigger_subject_role = models.ForeignKey('activities.ActivityRole', on_delete=models.SET_NULL, null=True, blank=True, related_name='subject_zones')
    trigger_notify_role = models.ForeignKey('activities.ActivityRole', on_delete=models.SET_NULL, null=True, blank=True, related_name='notify_zones')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_zones')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.name} in {self.activity.title}"


class MeetingPoint(models.Model):
    """Meeting-point details attached to a checkpoint.

    Keeping this as a separate one-to-one resource leaves room for future
    meeting-point-specific fields without coupling them to every checkpoint.
    """

    marker = models.OneToOneField(
        LocationMarker, on_delete=models.CASCADE, related_name='meeting_point'
    )
    name = models.CharField(max_length=200, default='Meeting point')
    description = models.TextField(blank=True, default='')
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ['start_time']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F('start_time')),
                name='meeting_point_end_after_start',
            ),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValidationError({'end_time': 'End time must be after start time.'})

    def __str__(self):
        return f"Meeting point at {self.marker.name}"


class LocationMarkerPhoto(models.Model):
    marker = models.ForeignKey(LocationMarker, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='location-markers/%Y/%m/')
    is_main = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_main', 'created_at']

    def save(self, *args, **kwargs):
        if not self.pk and not self.marker.photos.exists():
            self.is_main = True
        super().save(*args, **kwargs)
        if self.is_main:
            type(self).objects.filter(marker=self.marker).exclude(pk=self.pk).update(is_main=False)

    def delete(self, *args, **kwargs):
        marker = self.marker
        was_main = self.is_main
        result = super().delete(*args, **kwargs)
        if was_main:
            next_photo = marker.photos.order_by('created_at').first()
            if next_photo:
                next_photo.is_main = True
                next_photo.save(update_fields=['is_main'])
        return result

    def __str__(self):
        return f"Photo for {self.marker.name}"
