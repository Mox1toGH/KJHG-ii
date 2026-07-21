from django.contrib.auth import authenticate, get_user_model, password_validation
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserStatus, Friend
from .services import GoogleAuthService, TokenEmailService, blacklist_user_refresh_tokens


User = get_user_model()


class PublicUserSerializer(serializers.ModelSerializer):
    current_status = serializers.CharField(source='current_status.name', allow_null=True, read_only=True)
    created_at = serializers.DateTimeField(source='date_joined', read_only=True)
    last_seen = serializers.DateTimeField(source='last_login', allow_null=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'avatar', 'current_status', 'created_at', 'last_seen', 'hexagons_explored', 'checkpoints_visited')
        read_only_fields = fields


class UserSerializer(serializers.ModelSerializer):
    current_status = serializers.CharField(source='current_status.name', allow_null=True, read_only=True)
    created_at = serializers.DateTimeField(source='date_joined', read_only=True)
    last_seen = serializers.DateTimeField(source='last_login', allow_null=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'avatar', 'is_email_verified', 'auth_provider', 'current_status', 'created_at', 'last_seen', 'hexagons_explored', 'checkpoints_visited')
        read_only_fields = ('id', 'is_email_verified', 'auth_provider')


class UserStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStatus
        fields = ('id', 'name', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(_('Status name cannot be empty.'))
        user = self.context['request'].user
        queryset = UserStatus.objects.filter(user=user, name=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError(_('You already have a status with this name.'))
        return value


class CurrentStatusSerializer(serializers.Serializer):
    status_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_status_id(self, value):
        if value is None:
            return value
        try:
            status = UserStatus.objects.get(pk=value)
        except UserStatus.DoesNotExist as exc:
            raise serializers.ValidationError(_('Status not found.')) from exc
        if status.user_id != self.context['request'].user.pk:
            raise PermissionDenied(_('You can only select your own status.'))
        return value


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password')
        read_only_fields = ('id',)

    def validate_email(self, value):
        email = User.objects.normalize_email(value)
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(_('A user with this email already exists.'))
        return email

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(_('A user with this username already exists.'))
        return value

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.is_active = True
        user.is_email_verified = True
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    user = UserSerializer(read_only=True)

    def validate(self, attrs):
        request = self.context.get('request')
        user = authenticate(request=request, username=attrs['identifier'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError(_('Unable to log in with the provided credentials.'))

        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user,
        }


class EmailVerificationSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()

    def validate(self, attrs):
        user = TokenEmailService.verify_email(attrs['uid'], attrs['token'])
        if not user:
            raise serializers.ValidationError(_('Invalid or expired verification token.'))
        attrs['user'] = user
        return attrs


class EmailResendSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        return User.objects.normalize_email(value)

    def save(self, **kwargs):
        # Email resend disabled
        return


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        return User.objects.normalize_email(value)

    def save(self, **kwargs):
        # Password reset email disabled
        return


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        user = TokenEmailService.decode_user(attrs['uid'])
        if not user or not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError(_('Invalid or expired password reset token.'))
        password_validation.validate_password(attrs['new_password'], user)
        attrs['user'] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data['user']
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password'])
        blacklist_user_refresh_tokens(user)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate_current_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError(_('Current password is incorrect.'))
        return value

    def validate_new_password(self, value):
        password_validation.validate_password(value, self.context['request'].user)
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password'])
        blacklist_user_refresh_tokens(user)
        return user


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'avatar')

    def validate_email(self, value):
        email = User.objects.normalize_email(value)
        qs = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(_('A user with this email already exists.'))
        return email

    def validate_username(self, value):
        qs = User.objects.filter(username__iexact=value).exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(_('A user with this username already exists.'))
        return value

    def update(self, instance, validated_data):
        old_email = instance.email
        instance = super().update(instance, validated_data)
        if 'email' in validated_data and instance.email.lower() != old_email.lower():
            instance.is_email_verified = True
            instance.save(update_fields=['is_email_verified'])
        return instance


class DeleteAccountSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError(_('Password is incorrect.'))
        return value

    def save(self, **kwargs):
        self.context['request'].user.delete()


class GoogleLoginSerializer(serializers.Serializer):
    credential = serializers.CharField(write_only=True)
    user = UserSerializer(read_only=True)

    def validate(self, attrs):
        try:
            user = GoogleAuthService.authenticate(attrs['credential'])
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user,
        }


class FriendSerializer(serializers.ModelSerializer):
    friend = PublicUserSerializer(read_only=True)
    friend_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Friend
        fields = ('id', 'friend', 'friend_id', 'status', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_friend_id(self, value):
        if value == self.context['request'].user.pk:
            raise serializers.ValidationError(_('You cannot add yourself as a friend.'))
        try:
            User.objects.get(pk=value, is_active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError(_('User not found.'))
        return value

    def validate(self, attrs):
        user = self.context['request'].user
        friend_id = attrs.get('friend_id')
        if Friend.objects.filter(user=user, friend_id=friend_id).exists():
            raise serializers.ValidationError(_('A friend request already exists for this user.'))
        return attrs

    def create(self, validated_data):
        friend_id = validated_data.pop('friend_id')
        friend = User.objects.get(pk=friend_id)
        return Friend.objects.create(user=self.context['request'].user, friend=friend, status=Friend.Status.PENDING)


class FriendStatusSerializer(serializers.Serializer):
    is_friend = serializers.BooleanField(read_only=True)
