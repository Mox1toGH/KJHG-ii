from rest_framework import serializers

from .models import Notification, UserNotificationPreferences


class NotificationSerializer(serializers.ModelSerializer):
    is_read = serializers.BooleanField(read_only=True)

    class Meta:
        model = Notification
        fields = ('id', 'type', 'title', 'body', 'data', 'created_at', 'read_at', 'is_read')
        read_only_fields = fields


class UserNotificationPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotificationPreferences
        fields = ('email_enabled', 'in_app_enabled')
