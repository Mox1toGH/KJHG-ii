import math
import time
from rest_framework import viewsets, status, views
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q, F
from django.db import OperationalError, close_old_connections, connection
from django.conf import settings
from django.utils import timezone
from .models import Checkpoint, Route, RoutePoint, Visit, CheckpointPhoto, RoutePointPhoto, CheckpointQRCode
from .permissions import IsCheckpointQRCodeManager
from .selectors import get_checkpoint_qr_code_queryset, get_checkpoint_qr_codes, get_checkpoint_queryset
from .serializers import CheckpointQRCodeCreateSerializer, CheckpointQRCodeScanSerializer, CheckpointQRCodeSerializer
from .services import build_qr_codes_pdf, create_checkpoint_qr_code, delete_checkpoint_qr_code, scan_checkpoint_qr_code
from .serializers import CheckpointSerializer, RouteSerializer, RouteCreateSerializer, VisitSerializer, CheckpointPhotoSerializer, RoutePointPhotoSerializer
from activities.permissions import has_activity_permission, is_activity_owner
from activities.models import PermissionCode, Participant
from points.models import Point

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class CheckpointViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CheckpointSerializer

    def get_queryset(self):
        queryset = Checkpoint.objects.filter(
            Q(activity__participants__user=self.request.user) | Q(activity__created_by=self.request.user)
        ).select_related('activity', 'created_by__current_status', 'route').distinct()
        
        activity_id = self.request.query_params.get('activity_id')
        if activity_id:
            queryset = queryset.filter(activity_id=activity_id)
        return queryset

    def perform_create(self, serializer):
        activity = serializer.validated_data['activity']
        if not has_activity_permission(user=self.request.user, activity=activity, permission_code=PermissionCode.CREATE_CHECKPOINT):
            raise PermissionDenied('Your role cannot create checkpoints.')
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        checkpoint = self.get_object()
        if checkpoint.created_by_id != self.request.user.id and not is_activity_owner(
            user=self.request.user, activity=checkpoint.activity
        ):
            raise PermissionDenied('Only creator or Activity Owner can edit.')
        for attempt in range(3):
            try:
                serializer.save()
                return
            except OperationalError as error:
                if 'locked' not in str(error).lower() or attempt == 2:
                    raise
                close_old_connections()
                connection.close()
                time.sleep(0.25 * (attempt + 1))

    def perform_destroy(self, instance):
        if instance.created_by_id != self.request.user.id and not is_activity_owner(
            user=self.request.user, activity=instance.activity
        ):
            raise PermissionDenied('Only creator or Activity Owner can delete.')
        instance.delete()

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def photos(self, request, pk=None):
        checkpoint = self.get_object()
        if not has_activity_permission(user=request.user, activity=checkpoint.activity, permission_code=PermissionCode.UPLOAD_CHECKPOINT_PHOTOS):
            raise PermissionDenied('Your role cannot upload checkpoint photos.')
        serializer = CheckpointPhotoSerializer(data={'image': request.FILES.get('image'), 'is_main': request.data.get('is_main', False)})
        serializer.is_valid(raise_exception=True)
        serializer.save(checkpoint=checkpoint)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path=r'photos/(?P<photo_id>\d+)')
    def delete_photo(self, request, pk=None, photo_id=None):
        photo = self.get_object().photos.filter(pk=photo_id).first()
        if not photo:
            return Response({'detail': 'Photo not found.'}, status=status.HTTP_404_NOT_FOUND)
        photo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CheckpointQRCodeCollectionView(views.APIView):
    permission_classes = [IsAuthenticated, IsCheckpointQRCodeManager]

    def get_checkpoint(self, checkpoint_id):
        return get_object_or_404(get_checkpoint_queryset(), pk=checkpoint_id)

    def get(self, request, checkpoint_id):
        checkpoint = self.get_checkpoint(checkpoint_id)
        self.check_object_permissions(request, checkpoint)
        return Response(CheckpointQRCodeSerializer(
            get_checkpoint_qr_codes(checkpoint=checkpoint), many=True, context={'request': request}
        ).data)

    def post(self, request, checkpoint_id):
        checkpoint = self.get_checkpoint(checkpoint_id)
        self.check_object_permissions(request, checkpoint)
        serializer = CheckpointQRCodeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        qr_code = create_checkpoint_qr_code(
            checkpoint=checkpoint, created_by=request.user, name=serializer.validated_data.get('name'), points=serializer.validated_data.get('points', 0)
        )
        return Response(
            CheckpointQRCodeSerializer(qr_code, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class CheckpointQRCodeDeleteView(views.APIView):
    permission_classes = [IsAuthenticated, IsCheckpointQRCodeManager]

    def delete(self, request, pk):
        qr_code = get_object_or_404(get_checkpoint_qr_code_queryset(), pk=pk)
        self.check_object_permissions(request, qr_code)
        delete_checkpoint_qr_code(qr_code=qr_code)
        return Response(status=status.HTTP_204_NO_CONTENT)

class CheckpointQRCodeImageView(views.APIView):
    permission_classes = [IsAuthenticated, IsCheckpointQRCodeManager]

    def get(self, request, pk):
        qr_code = get_object_or_404(get_checkpoint_qr_code_queryset(), pk=pk)
        self.check_object_permissions(request, qr_code)
        return FileResponse(qr_code.image.open('rb'), as_attachment=True, content_type='image/png', filename=f'{qr_code.name}.png')


class CheckpointQRCodesPDFView(views.APIView):
    permission_classes = [IsAuthenticated, IsCheckpointQRCodeManager]

    def get(self, request, checkpoint_id):
        checkpoint = get_object_or_404(get_checkpoint_queryset(), pk=checkpoint_id)
        self.check_object_permissions(request, checkpoint)
        pdf = build_qr_codes_pdf(checkpoint=checkpoint, qr_codes=get_checkpoint_qr_codes(checkpoint=checkpoint))
        return FileResponse(pdf, as_attachment=True, content_type='application/pdf', filename=f'{checkpoint.name}-qrcodes.pdf')


class CheckpointQRCodeScanView(views.APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request):
        serializer = CheckpointQRCodeScanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        scan = scan_checkpoint_qr_code(user=request.user, **serializer.validated_data)
        return Response({'id': scan.id, 'scanned_at': scan.scanned_at}, status=status.HTTP_201_CREATED)

class RouteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RouteCreateSerializer
        return RouteSerializer

    def get_queryset(self):
        queryset = Route.objects.filter(
            Q(activity__participants__user=self.request.user) | Q(activity__created_by=self.request.user)
        ).select_related('activity', 'created_by__current_status', 'main_checkpoint').prefetch_related('points', 'points__photos').distinct()
        
        activity_id = self.request.query_params.get('activity_id')
        if activity_id:
            queryset = queryset.filter(activity_id=activity_id)
        return queryset

    def perform_create(self, serializer):
        activity = serializer.validated_data['activity']
        if not has_activity_permission(
            user=self.request.user,
            activity=activity,
            permission_code=PermissionCode.CREATE_ROUTE,
        ):
            raise PermissionDenied('Your role cannot create routes.')
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        route = self.get_object()
        if route.created_by_id != self.request.user.id and not is_activity_owner(
            user=self.request.user, activity=route.activity
        ):
            raise PermissionDenied('Only creator or Activity Owner can edit.')
        serializer.save()

    def perform_destroy(self, instance):
        if instance.created_by_id != self.request.user.id and not is_activity_owner(
            user=self.request.user, activity=instance.activity
        ):
            raise PermissionDenied('Only creator or Activity Owner can delete.')
        instance.delete()

class RoutePointViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = RoutePoint.objects.all()

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def photos(self, request, pk=None):
        route_point = self.get_object()
        if not has_activity_permission(user=request.user, activity=route_point.route.activity, permission_code=PermissionCode.UPLOAD_CHECKPOINT_PHOTOS):
            raise PermissionDenied('Your role cannot upload route photos.')
        serializer = RoutePointPhotoSerializer(data={'image': request.FILES.get('image'), 'is_main': request.data.get('is_main', False)})
        serializer.is_valid(raise_exception=True)
        serializer.save(route_point=route_point)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path=r'photos/(?P<photo_id>\d+)')
    def delete_photo(self, request, pk=None, photo_id=None):
        photo = self.get_object().photos.filter(pk=photo_id).first()
        if not photo:
            return Response({'detail': 'Photo not found.'}, status=status.HTTP_404_NOT_FOUND)
        photo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CheckInView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        point_type = request.data.get('type')
        point_id = request.data.get('id')
        lat = request.data.get('latitude')
        lng = request.data.get('longitude')
        accuracy = request.data.get('accuracy', 0)
        is_manual = request.data.get('is_manual', False)

        if not all([point_type, point_id, lat is not None, lng is not None]):
            return Response({'detail': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            lat = float(lat)
            lng = float(lng)
            accuracy = float(accuracy)
        except ValueError:
            return Response({'detail': 'Invalid coordinates.'}, status=status.HTTP_400_BAD_REQUEST)

        point = None
        activity = None
        is_main_checkpoint = False
        route = None

        if point_type == 'checkpoint':
            try:
                point = Checkpoint.objects.select_related('activity', 'route').get(id=point_id)
                activity = point.activity
                if hasattr(point, 'route'):
                    is_main_checkpoint = True
                    route = point.route
            except Checkpoint.DoesNotExist:
                return Response({'detail': 'Checkpoint not found.'}, status=status.HTTP_404_NOT_FOUND)
        elif point_type == 'route_point':
            try:
                point = RoutePoint.objects.select_related('route__activity').get(id=point_id)
                activity = point.route.activity
            except RoutePoint.DoesNotExist:
                return Response({'detail': 'Route point not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'detail': 'Invalid point type.'}, status=status.HTTP_400_BAD_REQUEST)

        participant = Participant.objects.filter(activity=activity, user=request.user).first()
        if not participant:
            return Response({'detail': 'You are not a participant in this activity.'}, status=status.HTTP_403_FORBIDDEN)

        if is_main_checkpoint and route:
            route_point_ids = list(route.points.values_list('id', flat=True))
            visited_route_point_ids = Visit.objects.filter(
                participant=participant,
                route_point_id__in=route_point_ids
            ).values_list('route_point_id', flat=True)
            
            if set(route_point_ids) != set(visited_route_point_ids):
                return Response({'detail': 'You must visit all route points before checking in to the main checkpoint.'}, status=status.HTTP_400_BAD_REQUEST)

        distance = calculate_distance(lat, lng, point.latitude, point.longitude)
        
        auto_acc_limit = getattr(settings, 'CHECKPOINT_AUTO_CHECKIN_ACCURACY', 50)
        manual_acc_limit = getattr(settings, 'CHECKPOINT_MAX_MANUAL_ACCURACY', 500)

        if distance > point.radius + accuracy:
            return Response({'detail': 'You are too far from the point.', 'needs_manual': False}, status=status.HTTP_400_BAD_REQUEST)

        if not is_manual:
            if accuracy > auto_acc_limit:
                return Response({'detail': 'Location accuracy is too low for automatic check-in. Please check in manually.', 'needs_manual': True}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if accuracy > manual_acc_limit:
                return Response({'detail': f'A more accurate location is required (accuracy > {manual_acc_limit}m).'}, status=status.HTTP_400_BAD_REQUEST)

        visit_kwargs = {
            'participant': participant,
            'checkpoint': point if point_type == 'checkpoint' else None,
            'route_point': point if point_type == 'route_point' else None,
        }
        
        visit, created = Visit.objects.update_or_create(
            **visit_kwargs,
            defaults={
                'is_manual': is_manual,
                'deviation': distance,
                'visited_at': timezone.now()
            }
        )

        # Increment checkpoints_visited counter for new visits
        if created:
            request.user.__class__.objects.filter(pk=request.user.pk).update(checkpoints_visited=F('checkpoints_visited') + 1)

        points_awarded = 0
        reward_points = getattr(point, 'points', 0) or 0
        if created and reward_points > 0:
            user_point, pt_created = Point.objects.get_or_create(
                user=request.user,
                room=activity,
                defaults={'points': reward_points},
            )
            if not pt_created:
                Point.objects.filter(pk=user_point.pk).update(points=F('points') + reward_points)
                user_point.refresh_from_db()
            points_awarded = reward_points

        user_point = Point.objects.filter(user=request.user, room=activity).first()
        response_data = VisitSerializer(visit).data
        response_data['points_awarded'] = points_awarded
        response_data['total_points'] = user_point.points if user_point else 0

        return Response(response_data, status=status.HTTP_200_OK)

class VisitViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = VisitSerializer

    def get_queryset(self):
        queryset = Visit.objects.filter(participant__user=self.request.user)

        activity_id = self.request.query_params.get('activity_id')
        if activity_id:
            queryset = queryset.filter(participant__activity_id=activity_id)
        return queryset
