from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from accounts.serializers import PublicUserSerializer
from .models import Activity, ActivityPermission, ActivityRole, Participant, PermissionCode, JoinRequest



class RolePermissionSerializer(serializers.Serializer):
    code = serializers.CharField(source='permission.code')
    name = serializers.CharField(source='permission.name', read_only=True)
    scope = serializers.JSONField(required=False, default=dict)


class ActivityPermissionInputSerializer(serializers.Serializer):
    code = serializers.CharField()
    scope = serializers.JSONField(required=False, default=dict)

class ActivityRoleSerializer(serializers.ModelSerializer):
    permissions = ActivityPermissionInputSerializer(many=True, required=False, write_only=True)
    permission_grants = serializers.SerializerMethodField()

    class Meta:
        model = ActivityRole
        fields = ['id', 'name', 'description', 'color', 'created_at', 'permissions', 'permission_grants']
        read_only_fields = ['id', 'created_at', 'permission_grants']

    def get_permission_grants(self, obj):
        return RolePermissionSerializer(obj.permission_grants.select_related('permission'), many=True).data

    def validate_permissions(self, value):
        codes = [item['code'] for item in value]
        permissions = {p.code: p for p in ActivityPermission.objects.filter(code__in=codes)}
        unknown = sorted(set(codes) - permissions.keys())
        if unknown:
            raise serializers.ValidationError({'code': _('Unknown permission(s): %(codes)s') % {'codes': ', '.join(unknown)}})
        normalized = []
        for item in value:
            scope = item.get('scope', {})
            if item['code'] == PermissionCode.VIEW_PARTICIPANTS_MAP:
                visibility = scope.get('visibility', 'everyone')
                if visibility not in ('everyone', 'roles'):
                    raise serializers.ValidationError(_('Map visibility must be everyone or roles.'))
                if visibility == 'roles' and not isinstance(scope.get('role_ids'), list):
                    raise serializers.ValidationError(_('role_ids is required when visibility is roles.'))
                if visibility == 'roles':
                    activity = self.context.get('activity')
                    valid_ids = {str(role.id) for role in ActivityRole.objects.filter(activity=activity)} if activity else set()
                    if not set(map(str, scope['role_ids'])) <= valid_ids:
                        raise serializers.ValidationError(_('Map visibility contains a role from another activity.'))
            normalized.append({'permission': permissions[item['code']], 'scope': scope})
        return normalized

class ParticipantSerializer(serializers.ModelSerializer):
    user_profile = PublicUserSerializer(source='user', read_only=True)
    role = ActivityRoleSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(
        source='role', queryset=ActivityRole.objects.all(), write_only=True, required=False, allow_null=True
    )
    
    class Meta:
        model = Participant
        fields = ['id', 'user', 'user_profile', 'role', 'role_id', 'joined_at']
        read_only_fields = ['id', 'user', 'role', 'joined_at']

    def validate_role_id(self, role):
        activity = self.context.get('activity')
        if activity and role and role.activity_id != activity.id:
            raise serializers.ValidationError(_('Role must belong to this activity.'))
        return role

class ActivitySerializer(serializers.ModelSerializer):
    participant_count = serializers.IntegerField(read_only=True, default=0)
    default_role_id = serializers.PrimaryKeyRelatedField(
        source='default_role', queryset=ActivityRole.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Activity
        fields = ['id', 'title', 'description', 'created_by', 'default_role_id', 'started_at', 'ended_at', 'status', 'participant_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def validate_default_role_id(self, role):
        activity = self.instance or self.context.get('activity')
        if activity and role and role.activity_id != activity.id:
            raise serializers.ValidationError(_('Default role must belong to this activity.'))
        if role and role.name.casefold() == 'owner':
            raise serializers.ValidationError(_('The Owner role cannot be the default participant role.'))
        return role


class JoinRequestSerializer(serializers.ModelSerializer):
    user_profile = PublicUserSerializer(source='user', read_only=True)
    activity_title = serializers.CharField(source='activity.title', read_only=True)
    
    class Meta:
        model = JoinRequest
        fields = ['id', 'activity', 'activity_title', 'user', 'user_profile', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'activity', 'user', 'status', 'created_at', 'updated_at']

