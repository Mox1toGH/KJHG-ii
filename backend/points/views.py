from django.db.models import Q
from rest_framework import permissions, viewsets
from .models import Point
from .serializers import PointSerializer


class PointViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PointSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Point.objects.filter(
            Q(room__participants__user=self.request.user) | Q(room__created_by=self.request.user)
        ).select_related('user', 'room').distinct()

        room_id = self.request.query_params.get('room_id')
        if room_id is not None:
            queryset = queryset.filter(room_id=room_id)
        return queryset
