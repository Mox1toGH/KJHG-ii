import uuid
from django.db import models
from django.contrib.auth import get_user_model
from activities.models import Activity

User = get_user_model()


class ShopItem(models.Model):
    class ItemType(models.TextChoices):
        AVATAR = 'AVATAR', 'Avatar'
        BADGE = 'BADGE', 'Badge'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item_type = models.CharField(max_length=20, choices=ItemType.choices)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='shop_items')
    price = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.item_type} - {self.activity.title}"


class AvatarItem(models.Model):
    shop_item = models.OneToOneField(ShopItem, on_delete=models.CASCADE, related_name='avatar')
    icon_file = models.FileField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"Avatar for {self.shop_item}"


class BadgeItem(models.Model):
    shop_item = models.OneToOneField(ShopItem, on_delete=models.CASCADE, related_name='badge')
    text = models.CharField(max_length=50)
    color = models.CharField(max_length=20, default='#3B82F6')

    def __str__(self):
        return f"Badge: {self.text} ({self.color})"


class UserItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchased_items')
    shop_item = models.ForeignKey(ShopItem, on_delete=models.CASCADE, related_name='user_items')
    is_equipped = models.BooleanField(default=False)
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'shop_item'], name='unique_user_shop_item')
        ]

    def __str__(self):
        return f"{self.user.username} - {self.shop_item.item_type} (equipped: {self.is_equipped})"
