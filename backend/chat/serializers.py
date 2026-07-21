from rest_framework import serializers

from accounts.serializers import PublicUserSerializer
from .models import ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = PublicUserSerializer(read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'activity', 'sender', 'body', 'created_at']
        read_only_fields = ['id', 'activity', 'sender', 'created_at']

    def validate_body(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Message cannot be empty.')
        return value
