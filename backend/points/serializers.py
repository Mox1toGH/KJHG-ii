from rest_framework import serializers
from .models import Point


class PointSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    display_name = serializers.SerializerMethodField()

    def get_display_name(self, obj):
        user = obj.user
        full_name = f'{user.first_name} {user.last_name}'.strip()
        return full_name or user.username

    class Meta:
        model = Point
        fields = ['id', 'user', 'username', 'display_name', 'room', 'points', 'created_at', 'updated_at']
        read_only_fields = fields
