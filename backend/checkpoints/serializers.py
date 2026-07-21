from rest_framework import serializers
from .models import Checkpoint, CheckpointPhoto, CheckpointQRCode, Route, RoutePoint, RoutePointPhoto, Visit
from .selectors import get_checkpoint_qr_progress
from activities.models import Participant
from shared.serializers import CreatedBySerializerMixin

class RoutePointSerializer(CreatedBySerializerMixin, serializers.ModelSerializer):
    photos = serializers.SerializerMethodField()
    # Allow id to be passed in on update so the backend can diff existing vs new points
    id = serializers.UUIDField(required=False, allow_null=True)
    created_by_name = serializers.SerializerMethodField()

    def get_photos(self, obj):
        return RoutePointPhotoSerializer(obj.photos.all(), many=True, context=self.context).data

    def get_created_by_name(self, obj):
        user = self.get_creator_user(obj)
        return f"{user.first_name} {user.last_name}".strip() or user.username if user else None

    class Meta:
        model = RoutePoint
        fields = ['id', 'route', 'sequence_number', 'name', 'points', 'description', 'latitude', 'longitude', 'radius', 'photos', 'created_by_name']
        read_only_fields = ['route']


class RouteSerializer(CreatedBySerializerMixin, serializers.ModelSerializer):
    points = RoutePointSerializer(many=True, read_only=True)
    created_by_name = serializers.SerializerMethodField()

    def get_created_by_name(self, obj):
        user = self.get_creator_user(obj)
        return f"{user.first_name} {user.last_name}".strip() or user.username if user else None
    
    class Meta:
        model = Route
        fields = ['id', 'activity', 'name', 'description', 'color', 'main_checkpoint', 'points', 'created_by', 'created_by_name', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']

class RouteCreateSerializer(CreatedBySerializerMixin, serializers.ModelSerializer):
    points = RoutePointSerializer(many=True)

    class Meta:
        model = Route
        fields = ['id', 'activity', 'name', 'description', 'color', 'main_checkpoint', 'points', 'created_by', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']

    def create(self, validated_data):
        points_data = validated_data.pop('points', [])
        route = Route.objects.create(**validated_data)
        for point_data in points_data:
            RoutePoint.objects.create(route=route, **point_data)
        return route

    def update(self, instance, validated_data):
        points_data = validated_data.pop('points', None)
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.color = validated_data.get('color', instance.color)
        instance.main_checkpoint = validated_data.get('main_checkpoint', instance.main_checkpoint)
        
        # Sync main checkpoint color
        instance.main_checkpoint.color = instance.color
        instance.main_checkpoint.save(update_fields=['color'])

        instance.save()

        if points_data is not None:
            # Diff points by ID to preserve existing ones (and their photos).
            existing_points = {str(p.id): p for p in instance.points.all()}

            # First pass: shift all existing sequence_numbers out of range to avoid
            # UNIQUE(route_id, sequence_number) collisions during reordering.
            for p in existing_points.values():
                p.sequence_number = 10000 + p.sequence_number
                p.save(update_fields=['sequence_number'])

            incoming_ids = set()

            for i, point_data in enumerate(points_data):
                point_id = str(point_data.pop('id', None) or '')
                point_data['sequence_number'] = i + 1
                if point_id and point_id in existing_points:
                    # Update in place — photos are preserved
                    point = existing_points[point_id]
                    for attr, value in point_data.items():
                        setattr(point, attr, value)
                    point.save()
                    incoming_ids.add(point_id)
                else:
                    # New point
                    new_point = RoutePoint.objects.create(route=instance, **point_data)
                    incoming_ids.add(str(new_point.id))

            # Delete points that were removed in the frontend
            for pid, point in existing_points.items():
                if pid not in incoming_ids:
                    point.delete()

        return instance


class CheckpointSerializer(CreatedBySerializerMixin, serializers.ModelSerializer):
    route = RouteSerializer(read_only=True)
    photos = serializers.SerializerMethodField()
    qr_progress = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()

    def get_photos(self, obj):
        return CheckpointPhotoSerializer(obj.photos.all(), many=True, context=self.context).data

    def get_qr_progress(self, obj):
        request = self.context.get('request')
        return get_checkpoint_qr_progress(checkpoint=obj, user=request.user if request else None)

    def get_created_by_name(self, obj):
        user = self.get_creator_user(obj)
        return f"{user.first_name} {user.last_name}".strip() or user.username if user else None

    class Meta:
        model = Checkpoint
        fields = ['id', 'activity', 'name', 'points', 'description', 'color', 'latitude', 'longitude', 'radius', 'route', 'photos', 'qr_progress', 'created_by', 'created_by_name', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']


class CheckpointQRCodeSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    scan_count = serializers.IntegerField(source='scans.count', read_only=True)

    def get_image(self, obj):
        request = self.context.get('request')
        from django.urls import reverse
        url = reverse('checkpoint-qrcode-image', kwargs={'pk': obj.pk})
        return request.build_absolute_uri(url) if request else url

    class Meta:
        model = CheckpointQRCode
        fields = ['id', 'checkpoint', 'name', 'image', 'scan_count', 'points', 'created_by', 'created_at']
        read_only_fields = ['id', 'checkpoint', 'image', 'created_by', 'created_at']


class CheckpointQRCodeCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200, required=False, allow_blank=True)
    points = serializers.IntegerField(default=0, min_value=0)


class CheckpointQRCodeScanSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    latitude = serializers.FloatField(min_value=-90, max_value=90)
    longitude = serializers.FloatField(min_value=-180, max_value=180)


class VisitSerializer(serializers.ModelSerializer):
    participant_id = serializers.UUIDField(source='participant.id', read_only=True)
    
    class Meta:
        model = Visit
        fields = ['id', 'participant_id', 'checkpoint', 'route_point', 'visited_at', 'is_manual', 'deviation']
        read_only_fields = ['id', 'participant_id', 'visited_at', 'is_manual', 'deviation']


class CheckpointPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckpointPhoto
        fields = ['id', 'image', 'is_main', 'created_at']
        read_only_fields = ['id', 'created_at']


class RoutePointPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoutePointPhoto
        fields = ['id', 'image', 'is_main', 'created_at']
        read_only_fields = ['id', 'created_at']
