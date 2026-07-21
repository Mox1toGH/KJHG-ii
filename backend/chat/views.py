from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from activities.models import Activity
from activities.permissions import IsActivityParticipant
from .models import ChatMessage
from .serializers import ChatMessageSerializer
from .services import create_chat_message


class ActivityChatMessageViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_activity(self, request, activity_pk):
        activity = get_object_or_404(Activity, pk=activity_pk)
        if not IsActivityParticipant().has_object_permission(request, self, activity):
            return None
        return activity

    def list(self, request, activity_pk=None):
        activity = self.get_activity(request, activity_pk)
        if activity is None:
            return Response(status=status.HTTP_403_FORBIDDEN)

        queryset = ChatMessage.objects.filter(activity=activity).select_related(
            'sender', 'sender__current_status'
        ).order_by('-created_at')[:100]
        messages = list(reversed(queryset))
        return Response(ChatMessageSerializer(messages, many=True).data)

    def create(self, request, activity_pk=None):
        activity = self.get_activity(request, activity_pk)
        if activity is None:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = ChatMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = create_chat_message(
            activity=activity,
            sender=request.user,
            body=serializer.validated_data['body'],
        )
        return Response(ChatMessageSerializer(message).data, status=status.HTTP_201_CREATED)
