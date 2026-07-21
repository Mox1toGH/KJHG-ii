from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class MapObjectCreatorSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    current_status = serializers.CharField(source='current_status.name', allow_null=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'display_name', 'avatar', 'current_status')
        read_only_fields = fields

    def get_display_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'.strip() or obj.username


class CreatedBySerializerMixin:
    """Adds one nullable creator contract to every Activity map-object API."""

    def get_creator_user(self, instance):
        creator = getattr(instance, 'created_by', None)
        if creator is not None:
            return creator
        marker = getattr(instance, 'marker', None)
        if marker is not None:
            return getattr(marker, 'created_by', None)
        route = getattr(instance, 'route', None)
        return getattr(route, 'created_by', None) if route is not None else None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return self.add_creator(data, instance)

    def add_creator(self, data, instance):
        creator = self.get_creator_user(instance)
        data['creator'] = MapObjectCreatorSerializer(creator, context=self.context).data if creator else None
        return data
