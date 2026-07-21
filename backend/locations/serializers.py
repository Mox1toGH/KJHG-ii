from rest_framework import serializers
from .models import ActivityZone, LocationMarker, LocationMarkerPhoto, MeetingPoint
from shared.serializers import CreatedBySerializerMixin


def validate_zone_points(value):
    if not isinstance(value, list) or len(value) < 3:
        raise serializers.ValidationError('A zone needs at least three points.')

    for point in value:
        if not isinstance(point, list) or len(point) != 2:
            raise serializers.ValidationError('Each zone point must be [longitude, latitude].')
        longitude, latitude = point
        if not isinstance(longitude, (int, float)) or not isinstance(latitude, (int, float)):
            raise serializers.ValidationError('Zone point coordinates must be numbers.')
        if longitude < -180 or longitude > 180 or latitude < -90 or latitude > 90:
            raise serializers.ValidationError('Zone point coordinates are out of range.')

    return value


class LocationMarkerPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationMarkerPhoto
        fields = ['id', 'image', 'is_main', 'created_at']
        read_only_fields = ['id', 'created_at']


class MeetingPointSerializer(serializers.ModelSerializer):
    start_time = serializers.TimeField(format='%H:%M', input_formats=['%H:%M', '%H:%M:%S'])
    end_time = serializers.TimeField(format='%H:%M', input_formats=['%H:%M', '%H:%M:%S'])
    class Meta:
        model = MeetingPoint
        fields = ['name', 'description', 'start_time', 'end_time']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Keep the pre-name/description response shape for legacy records and
        # clients, while exposing the new fields as soon as they are used.
        if instance.name == 'Meeting point' and not instance.description:
            data.pop('name', None)
            data.pop('description', None)
        return data

    def validate(self, attrs):
        if attrs.get('start_time') and attrs.get('end_time') and attrs['end_time'] <= attrs['start_time']:
            raise serializers.ValidationError({'end_time': 'End time must be after start time.'})
        return attrs


class ActivityZoneSerializer(CreatedBySerializerMixin, serializers.ModelSerializer):
    points = serializers.JSONField(validators=[validate_zone_points])

    class Meta:
        model = ActivityZone
        fields = ['id', 'activity', 'name', 'color', 'points', 'trigger_action', 'trigger_subject_role', 'trigger_notify_role', 'created_by', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']


class LocationMarkerSerializer(CreatedBySerializerMixin, serializers.ModelSerializer):
    photos = LocationMarkerPhotoSerializer(many=True, read_only=True)
    meeting_point = MeetingPointSerializer(required=False, allow_null=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = LocationMarker
        fields = ['id', 'activity', 'name', 'description', 'color', 'latitude', 'longitude', 'created_by', 'created_by_name', 'created_at', 'photos', 'meeting_point']
        read_only_fields = ['id', 'created_by', 'created_at']

    def get_created_by_name(self, obj):
        user = self.get_creator_user(obj)
        return f"{user.first_name} {user.last_name}".strip() or user.username if user else None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Query by FK so a just-created/deleted reverse relation is not hidden
        # by Django's related-object cache on the marker instance.
        meeting_point = MeetingPoint.objects.filter(marker_id=instance.pk).first()
        data['meeting_point'] = MeetingPointSerializer(meeting_point).data if meeting_point else None
        return self.add_creator(data, instance)

    def create(self, validated_data):
        meeting_point_data = validated_data.pop('meeting_point', None)
        marker = super().create(validated_data)
        if meeting_point_data is not None:
            MeetingPoint.objects.create(marker=marker, **meeting_point_data)
        return marker

    def update(self, instance, validated_data):
        meeting_point_data = validated_data.pop('meeting_point', serializers.empty)
        marker = super().update(instance, validated_data)
        if meeting_point_data is not serializers.empty:
            if meeting_point_data is None:
                MeetingPoint.objects.filter(marker=marker).delete()
            else:
                MeetingPoint.objects.update_or_create(marker=marker, defaults=meeting_point_data)
        return marker
