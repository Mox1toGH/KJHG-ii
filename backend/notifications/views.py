from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from . import services
from .models import Notification, UserNotificationPreferences
from .serializers import NotificationSerializer, UserNotificationPreferencesSerializer


class NotificationViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.active().filter(user=self.request.user).order_by('-created_at')

    def list(self, request):
        return Response(NotificationSerializer(self.get_queryset(), many=True).data)

    @action(detail=True, methods=['post'], url_path='read')
    def read(self, request, pk=None):
        notification = self.get_object()
        services.mark_as_read(notification=notification, user=request.user)
        return Response(NotificationSerializer(notification).data)

    @action(detail=False, methods=['post'], url_path='read-all')
    def read_all(self, request):
        services.mark_all_as_read(user=request.user)
        return Response({'detail': 'All notifications marked as read.'})

    def destroy(self, request, pk=None):
        services.soft_delete(notification=self.get_object(), user=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], url_path='clear')
    def clear(self, request):
        services.clear_all(user=request.user)
        return Response({'detail': 'All notifications cleared.'})

    @action(detail=False, methods=['get', 'put'], url_path='preferences')
    def preferences(self, request):
        preferences, created = UserNotificationPreferences.objects.get_or_create(
            user=request.user
        )
        
        if request.method == 'GET':
            return Response(UserNotificationPreferencesSerializer(preferences).data)
        
        serializer = UserNotificationPreferencesSerializer(
            preferences, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
