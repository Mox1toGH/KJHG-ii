from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from activities.models import Participant
from activities.permissions import participant_map_scope
from activities.models import Activity
from .serializers import ParticipantLocationSerializer
from .permissions import IsActivityParticipant
from .services import set_participant_sos

class ParticipantLocationListView(generics.ListAPIView):
    serializer_class = ParticipantLocationSerializer
    permission_classes = [IsActivityParticipant]
    pagination_class = None  # Return all locations

    def get_queryset(self):
        activity_id = self.kwargs['activity_id']
        activity = Activity.objects.get(pk=activity_id)
        self.activity = activity
        role_ids = participant_map_scope(user=self.request.user, activity=activity)
        queryset = Participant.objects.filter(activity_id=activity_id)
        if role_ids is not None:
            queryset = queryset.filter(Q(user=self.request.user) | Q(role_id__in=role_ids))
        return queryset.select_related(
            'user', 'role', 'location'
        )


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def participant_sos_view(request, activity_id):
    participant = get_object_or_404(
        Participant.objects.select_related('activity', 'user'),
        activity_id=activity_id,
        user=request.user,
    )
    if request.method == 'GET':
        return Response({'active': participant.sos_active, 'activated_at': participant.sos_activated_at})
    active = request.data.get('active')
    if not isinstance(active, bool):
        return Response({'active': ['This field must be a boolean.']}, status=status.HTTP_400_BAD_REQUEST)
    participant = set_participant_sos(participant=participant, active=active)
    return Response({
        'active': participant.sos_active,
        'activated_at': participant.sos_activated_at,
    })
