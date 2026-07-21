from rest_framework import serializers
from activities.models import Participant
from .models import ParticipantLocation

class LocationDataSerializer(serializers.ModelSerializer):
    # GeoJSON/MapLibre expects numeric coordinates, never decimal strings.
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()

    class Meta:
        model = ParticipantLocation
        fields = ['latitude', 'longitude', 'accuracy', 'heading', 'speed']

class ParticipantLocationSerializer(serializers.ModelSerializer):
    participant_id = serializers.UUIDField(source='id', read_only=True)
    user = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    last_updated = serializers.SerializerMethodField()

    class Meta:
        model = Participant
        fields = ['participant_id', 'user', 'role', 'location', 'last_updated', 'sos_active', 'sos_activated_at']

    def get_user(self, obj):
        return {
            "id": str(obj.user.id),
            "username": obj.user.username,
            "display_name": ' '.join(filter(None, [obj.user.first_name, obj.user.last_name])),
        }

    def get_role(self, obj):
        if obj.role:
            return {
                "id": str(obj.role.id),
                "name": obj.role.name
            }
        return None

    def get_location(self, obj):
        location = getattr(obj, 'location', None)
        return LocationDataSerializer(location).data if location else None

    def get_last_updated(self, obj):
        location = getattr(obj, 'location', None)
        return location.updated_at if location else None

    def get_sos_active(self, obj):
        return obj.sos_active

    def get_sos_activated_at(self, obj):
        return obj.sos_activated_at
