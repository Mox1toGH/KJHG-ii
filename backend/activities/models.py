import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class PermissionCode(models.TextChoices):
    CREATE_CHECKPOINT = 'checkpoints.create', _('Create checkpoints')
    CREATE_LOCATION = 'locations.create', _('Create checkpoints/locations')
    CREATE_ROUTE = 'routes.create', _('Create routes')
    MANAGE_CHECKPOINT_QRCODES = 'checkpoints.qrcodes.manage', _('Manage checkpoint QR codes')
    UPLOAD_CHECKPOINT_PHOTOS = 'checkpoints.photos.upload', _('Upload photos to checkpoints/locations')
    SET_MEETING_POINTS = 'meeting_points.set', _('Set meeting points')
    VIEW_PARTICIPANTS_MAP = 'participants.map.view', _('View participants on the map')

class Activity(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        ACTIVE = 'ACTIVE', _('Active')
        FINISHED = 'FINISHED', _('Finished')
        CANCELLED = 'CANCELLED', _('Cancelled')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    description = models.TextField(blank=True, default='', verbose_name=_('Description'))
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_activities', verbose_name=_('Created by'))
    started_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Started at'))
    ended_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Ended at'))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, verbose_name=_('Status'))
    default_role = models.ForeignKey(
        'ActivityRole',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='default_for_activities',
        verbose_name=_('Default role'),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Activity')
        verbose_name_plural = _('Activities')

    def __str__(self):
        return self.title

class ActivityRole(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='roles', verbose_name=_('Activity'))
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    description = models.TextField(blank=True, default='', verbose_name=_('Description'))
    color = models.CharField(max_length=20, blank=True, default='', verbose_name=_('Color'))
    permissions = models.ManyToManyField(
        'ActivityPermission', through='RolePermission', related_name='roles', blank=True, verbose_name=_('Permissions')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Activity Role')
        verbose_name_plural = _('Activity Roles')
        constraints = [
            models.UniqueConstraint(fields=['activity', 'name'], name='unique_activity_role_name')
        ]

    def __str__(self):
        return f"{self.name} - {self.activity.title}"


class ActivityPermission(models.Model):
    """The permission catalog. Adding a permission is a data/model change only."""
    code = models.CharField(max_length=100, unique=True, verbose_name=_('Code'))
    name = models.CharField(max_length=200, verbose_name=_('Name'))
    description = models.TextField(blank=True, default='', verbose_name=_('Description'))

    class Meta:
        ordering = ['code']
        verbose_name = _('Activity Permission')
        verbose_name_plural = _('Activity Permissions')

    def __str__(self):
        return self.code


class RolePermission(models.Model):
    """A role's grant, with room for permission-specific configuration."""
    role = models.ForeignKey(ActivityRole, on_delete=models.CASCADE, related_name='permission_grants', verbose_name=_('Role'))
    permission = models.ForeignKey(ActivityPermission, on_delete=models.CASCADE, related_name='role_grants', verbose_name=_('Permission'))
    scope = models.JSONField(default=dict, blank=True, verbose_name=_('Scope'))

    class Meta:
        verbose_name = _('Role Permission')
        verbose_name_plural = _('Role Permissions')
        constraints = [
            models.UniqueConstraint(fields=['role', 'permission'], name='unique_role_permission'),
        ]

class Participant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='participants', verbose_name=_('Activity'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='participations', verbose_name=_('User'))
    role = models.ForeignKey(ActivityRole, on_delete=models.SET_NULL, null=True, blank=True, related_name='participants', verbose_name=_('Role'))
    current_zones = models.ManyToManyField('locations.ActivityZone', blank=True, related_name='current_participants', verbose_name=_('Current zones'))
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Joined at'))
    sos_active = models.BooleanField(default=False, verbose_name=_('SOS active'))
    sos_activated_at = models.DateTimeField(null=True, blank=True, verbose_name=_('SOS activated at'))

    class Meta:
        verbose_name = _('Participant')
        verbose_name_plural = _('Participants')
        constraints = [
            models.UniqueConstraint(fields=['activity', 'user'], name='unique_activity_user')
        ]

    def __str__(self):
        return f"{self.user.email} in {self.activity.title}"


class JoinRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        ACCEPTED = 'ACCEPTED', _('Accepted')
        REJECTED = 'REJECTED', _('Rejected')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='join_requests', verbose_name=_('Activity'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='join_requests', verbose_name=_('User'))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name=_('Status'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Join Request')
        verbose_name_plural = _('Join Requests')
        constraints = [
            models.UniqueConstraint(fields=['activity', 'user'], name='unique_activity_user_join_request')
        ]

    def __str__(self):
        return f"{self.user.email} -> {self.activity.title} ({self.status})"

