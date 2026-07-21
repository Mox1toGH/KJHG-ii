import uuid
from django.db import models
from django.contrib.auth import get_user_model
from activities.models import Activity

User = get_user_model()

class Point(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='room_points')
    room = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='points')
    points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'room'], name='unique_user_room_points')
        ]

    def __str__(self):
        return f"{self.user.username} in room {self.room.title}: {self.points}"
