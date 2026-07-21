from rest_framework import permissions
from activities.models import Participant

class IsActivityParticipant(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        activity_id = view.kwargs.get('activity_id')
        if not activity_id:
            return False
        return Participant.objects.filter(
            activity_id=activity_id, user=request.user
        ).exists()
