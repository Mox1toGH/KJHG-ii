from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Activity, ActivityRole, Participant, JoinRequest
from .serializers import ActivitySerializer, ActivityRoleSerializer, ParticipantSerializer, JoinRequestSerializer
from . import services
from . import selectors
from .permissions import IsActivityOwner, IsActivityParticipant

class ActivityViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        activities = selectors.get_activities_for_user(user=request.user)
        serializer = ActivitySerializer(activities, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        activity = get_object_or_404(Activity, pk=pk)
        if not IsActivityParticipant().has_object_permission(request, self, activity):
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = ActivitySerializer(activity)
        return Response(serializer.data)

    def create(self, request):
        serializer = ActivitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        activity = services.create_activity(
            user=request.user,
            **serializer.validated_data
        )
        return Response(ActivitySerializer(activity).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk=None):
        activity = get_object_or_404(Activity, pk=pk)
        if not IsActivityOwner().has_object_permission(request, self, activity):
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        serializer = ActivitySerializer(activity, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        activity = services.update_activity(
            activity=activity,
            **serializer.validated_data
        )
        return Response(ActivitySerializer(activity).data)

    def destroy(self, request, pk=None):
        activity = get_object_or_404(Activity, pk=pk)
        if not IsActivityOwner().has_object_permission(request, self, activity):
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        services.delete_activity(activity=activity)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        activity = get_object_or_404(Activity, pk=pk)
        services.join_activity(activity=activity, user=request.user)
        return Response({"detail": "Запит на приєднання надіслано власнику кімнати"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        activity = get_object_or_404(Activity, pk=pk)
        services.leave_activity(activity=activity, user=request.user)
        return Response({"detail": "Successfully left"}, status=status.HTTP_200_OK)

class ActivityRoleViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request, activity_pk=None):
        activity = get_object_or_404(Activity, pk=activity_pk)
        if not IsActivityParticipant().has_object_permission(request, self, activity):
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        roles = selectors.get_activity_roles(activity=activity)
        serializer = ActivityRoleSerializer(roles, many=True)
        return Response(serializer.data)

    def create(self, request, activity_pk=None):
        activity = get_object_or_404(Activity, pk=activity_pk)
        if not IsActivityOwner().has_object_permission(request, self, activity):
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        serializer = ActivityRoleSerializer(data=request.data, context={'activity': activity})
        serializer.is_valid(raise_exception=True)
        
        role = services.create_activity_role(
            activity=activity,
            **serializer.validated_data
        )
        return Response(ActivityRoleSerializer(role).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk=None, activity_pk=None):
        activity = get_object_or_404(Activity, pk=activity_pk)
        if not IsActivityOwner().has_object_permission(request, self, activity):
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        role = get_object_or_404(ActivityRole, pk=pk, activity=activity)
        
        serializer = ActivityRoleSerializer(role, data=request.data, partial=True, context={'activity': activity})
        serializer.is_valid(raise_exception=True)
        
        role = services.update_activity_role(
            role=role,
            **serializer.validated_data
        )
        return Response(ActivityRoleSerializer(role).data)

    def destroy(self, request, pk=None, activity_pk=None):
        activity = get_object_or_404(Activity, pk=activity_pk)
        if not IsActivityOwner().has_object_permission(request, self, activity):
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        role = get_object_or_404(ActivityRole, pk=pk, activity=activity)
        services.delete_activity_role(role=role)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ParticipantViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request, activity_pk=None):
        activity = get_object_or_404(Activity, pk=activity_pk)
        if not IsActivityParticipant().has_object_permission(request, self, activity):
            return Response(status=status.HTTP_403_FORBIDDEN)
        participants = Participant.objects.filter(activity=activity).select_related('user', 'role')
        return Response(ParticipantSerializer(participants, many=True).data)

    def partial_update(self, request, pk=None, activity_pk=None):
        activity = get_object_or_404(Activity, pk=activity_pk)
        if not IsActivityOwner().has_object_permission(request, self, activity):
            return Response(status=status.HTTP_403_FORBIDDEN)
        participant = get_object_or_404(Participant, pk=pk, activity=activity)
        serializer = ParticipantSerializer(participant, data=request.data, partial=True, context={'activity': activity})
        serializer.is_valid(raise_exception=True)
        participant = services.assign_participant_role(
            participant=participant, role=serializer.validated_data.get('role', participant.role)
        )
        return Response(ParticipantSerializer(participant).data)

    def destroy(self, request, pk=None, activity_pk=None):
        activity = get_object_or_404(Activity, pk=activity_pk)
        if not IsActivityOwner().has_object_permission(request, self, activity):
            return Response(status=status.HTTP_403_FORBIDDEN)
        participant = get_object_or_404(Participant, pk=pk, activity=activity)
        services.remove_participant(participant=participant)
        return Response(status=status.HTTP_204_NO_CONTENT)


class JoinRequestViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        direction = request.query_params.get('direction', 'incoming')
        if direction == 'incoming':
            # requests sent to rooms owned by the user
            queryset = JoinRequest.objects.filter(
                activity__created_by=request.user,
                status=JoinRequest.Status.PENDING
            ).select_related('user', 'activity')
        else:
            # outgoing requests sent by the user
            queryset = JoinRequest.objects.filter(
                user=request.user,
                status=JoinRequest.Status.PENDING
            ).select_related('activity')
        
        serializer = JoinRequestSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        join_request = get_object_or_404(JoinRequest, pk=pk)
        if join_request.activity.created_by != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        services.approve_join_request(join_request=join_request)
        return Response({"detail": "Запит прийнято"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        join_request = get_object_or_404(JoinRequest, pk=pk)
        if join_request.activity.created_by != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        services.reject_join_request(join_request=join_request)
        return Response({"detail": "Запит відхилено"}, status=status.HTTP_200_OK)

