import logging

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from .models import ActivityZone, LocationMarker, MeetingPoint
from .serializers import ActivityZoneSerializer, LocationMarkerPhotoSerializer, LocationMarkerSerializer
from activities.permissions import has_activity_permission, is_activity_owner
from activities.models import PermissionCode
from activities.selectors import get_activities_for_user

logger = logging.getLogger(__name__)

class ActivityZoneViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ActivityZoneSerializer

    def get_queryset(self):
        queryset = ActivityZone.objects.filter(
            Q(activity__participants__user=self.request.user) | Q(activity__created_by=self.request.user)
        ).select_related('activity', 'created_by__current_status').distinct()

        activity_id = self.request.query_params.get('activity_id')
        if activity_id:
            queryset = queryset.filter(activity_id=activity_id)

        return queryset

    def perform_create(self, serializer):
        activity = serializer.validated_data['activity']
        if not has_activity_permission(
            user=self.request.user,
            activity=activity,
            permission_code=PermissionCode.CREATE_LOCATION,
        ):
            raise PermissionDenied('Your role cannot create zones in this activity.')
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        zone = self.get_object()
        if zone.created_by_id != self.request.user.id and not is_activity_owner(
            user=self.request.user, activity=zone.activity
        ):
            raise PermissionDenied('Only the zone creator or Activity Owner can edit it.')
        serializer.save()

    def perform_destroy(self, instance):
        if instance.created_by_id != self.request.user.id and not is_activity_owner(
            user=self.request.user, activity=instance.activity
        ):
            raise PermissionDenied('Only the zone creator or Activity Owner can delete it.')
        instance.delete()


class LocationMarkerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = LocationMarkerSerializer

    def get_queryset(self):
        queryset = LocationMarker.objects.filter(
            Q(activity__participants__user=self.request.user) | Q(activity__created_by=self.request.user)
        ).select_related('activity', 'created_by__current_status', 'meeting_point').distinct()
        
        activity_id = self.request.query_params.get('activity_id')
        if activity_id:
            queryset = queryset.filter(activity_id=activity_id)
            
        return queryset

    def perform_create(self, serializer):
        activity = serializer.validated_data['activity']
        has_create_permission = has_activity_permission(
            user=self.request.user, activity=activity,
            permission_code=PermissionCode.CREATE_LOCATION,
        )
        has_meeting_point_permission = has_activity_permission(
            user=self.request.user,
            activity=activity,
            permission_code=PermissionCode.SET_MEETING_POINTS,
        ) if serializer.validated_data.get('meeting_point') is not None else True
        logger.info(
            '[locations] marker create user=%s activity=%s fields=%s '
            'meeting_point=%r create_permission=%s meeting_point_permission=%s',
            self.request.user.pk,
            activity.pk,
            sorted(serializer.validated_data.keys()),
            serializer.validated_data.get('meeting_point'),
            has_create_permission,
            has_meeting_point_permission,
        )
        if not has_create_permission:
            raise PermissionDenied('Your role cannot create checkpoints in this activity.')
        if not has_meeting_point_permission:
            raise PermissionDenied('Your role cannot set meeting points in this activity.')
        serializer.save(created_by=self.request.user)
        logger.info('[locations] marker created user=%s activity=%s', self.request.user.pk, activity.pk)

    def perform_update(self, serializer):
        marker = self.get_object()
        logger.info(
            '[locations] marker update user=%s marker=%s fields=%s meeting_point=%r',
            self.request.user.pk,
            marker.pk,
            sorted(serializer.validated_data.keys()),
            serializer.validated_data.get('meeting_point', '<omitted>'),
        )
        if 'meeting_point' in serializer.validated_data:
            requested_meeting_point = serializer.validated_data['meeting_point']
            current_meeting_point = MeetingPoint.objects.filter(marker=marker).values(
                'start_time', 'end_time'
            ).first()
            meeting_point_changed = (
                None if requested_meeting_point is None else {
                    'start_time': requested_meeting_point['start_time'],
                    'end_time': requested_meeting_point['end_time'],
                }
            ) != current_meeting_point
            logger.info(
                '[locations] meeting point comparison marker=%s current=%r requested=%r changed=%s',
                marker.pk,
                current_meeting_point,
                requested_meeting_point,
                meeting_point_changed,
            )
            if meeting_point_changed and not has_activity_permission(
                user=self.request.user,
                activity=marker.activity,
                permission_code=PermissionCode.SET_MEETING_POINTS,
            ):
                raise PermissionDenied('Your role cannot set meeting points in this activity.')
        if marker.created_by_id != self.request.user.id and not is_activity_owner(
            user=self.request.user, activity=marker.activity
        ):
            raise PermissionDenied('Only the checkpoint creator or Activity Owner can edit it.')
        serializer.save()

    def perform_destroy(self, instance):
        if instance.created_by_id != self.request.user.id and not is_activity_owner(
            user=self.request.user, activity=instance.activity
        ):
            raise PermissionDenied('Only the checkpoint creator or Activity Owner can delete it.')
        instance.delete()
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def photos(self, request, pk=None):
        marker = self.get_object()
        if not has_activity_permission(
            user=request.user,
            activity=marker.activity,
            permission_code=PermissionCode.UPLOAD_CHECKPOINT_PHOTOS,
        ):
            raise PermissionDenied('Your role cannot upload photos to checkpoints.')
        serializer = LocationMarkerPhotoSerializer(data={
            'image': request.FILES.get('image'),
            'is_main': request.data.get('is_main', False),
        })
        serializer.is_valid(raise_exception=True)
        serializer.save(marker=marker)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path=r'photos/(?P<photo_id>\d+)')
    def delete_photo(self, request, pk=None, photo_id=None):
        marker = self.get_object()
        photo = marker.photos.filter(pk=photo_id).first()
        if photo is None:
            return Response({'detail': 'Photo not found.'}, status=status.HTTP_404_NOT_FOUND)
        photo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
