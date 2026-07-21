import uuid

from django.conf import settings
from django.db import models


class ScratchDiscovery(models.Model):
    """A permanent H3 cell discovered by one user."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='scratch_discoveries',
    )
    h3_index = models.CharField(max_length=16)
    latitude = models.FloatField()
    longitude = models.FloatField()
    discovered_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['discovered_at', 'id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'h3_index'],
                name='scratch_discovery_user_h3_unique',
            ),
        ]
        indexes = [
            models.Index(fields=['user'], name='scratch_disc_user_idx'),
            models.Index(fields=['h3_index'], name='scratch_disc_h3_idx'),
            models.Index(fields=['user', 'discovered_at'], name='scratch_disc_user_date_idx'),
        ]

    def __str__(self):
        return f'{self.user_id}:{self.h3_index}'
