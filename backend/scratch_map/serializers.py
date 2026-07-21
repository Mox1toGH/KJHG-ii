from rest_framework import serializers

from .config import H3_RESOLUTION
from .models import ScratchDiscovery


class ScratchDiscoverySerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = ScratchDiscovery
        fields = ('id', 'user_id', 'h3_index', 'discovered_at')
        read_only_fields = fields


class ScratchDiscoveryInputSerializer(serializers.Serializer):
    latitude = serializers.FloatField(min_value=-90, max_value=90)
    longitude = serializers.FloatField(min_value=-180, max_value=180)


class ScratchMapStatisticsSerializer(serializers.Serializer):
    total_discovered_cells = serializers.IntegerField()
    today_discoveries = serializers.IntegerField()
    weekly_discoveries = serializers.IntegerField()
    monthly_discoveries = serializers.IntegerField()
    total_explored_area_km2 = serializers.FloatField()


class ScratchMapConfigSerializer(serializers.Serializer):
    h3_resolution = serializers.IntegerField(default=H3_RESOLUTION)
