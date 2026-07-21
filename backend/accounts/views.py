from django.contrib.auth import get_user_model
from django.conf import settings
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import generics, permissions, status, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .cookies import delete_auth_cookies, set_auth_cookies
from .serializers import (
    ChangePasswordSerializer,
    DeleteAccountSerializer,
    EmailResendSerializer,
    EmailVerificationSerializer,
    GoogleLoginSerializer,
    LoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
    PublicUserSerializer,
    RegisterSerializer,
    UpdateProfileSerializer,
    UserSerializer,
    UserStatusSerializer,
    CurrentStatusSerializer,
    FriendSerializer,
    FriendStatusSerializer,
)
from .models import UserStatus, Friend


User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {'detail': _('Registration successful. Please verify your email address.')},
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


@method_decorator(csrf_protect, name='dispatch')
class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        response = Response({'detail': _('Login successful')})
        set_auth_cookies(
            response,
            serializer.validated_data['access'],
            serializer.validated_data['refresh'],
        )
        return response


@method_decorator(csrf_protect, name='dispatch')
class RefreshView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        refresh = request.COOKIES.get(settings.JWT_COOKIE_REFRESH)
        serializer = TokenRefreshSerializer(data={'refresh': refresh})
        serializer.is_valid(raise_exception=True)

        response = Response({'detail': _('Token refreshed')})
        set_auth_cookies(
            response,
            serializer.validated_data['access'],
            serializer.validated_data.get('refresh'),
        )
        return response


@method_decorator(csrf_protect, name='dispatch')
class LogoutView(APIView):
    def post(self, request):
        refresh = request.COOKIES.get(settings.JWT_COOKIE_REFRESH)
        if refresh:
            try:
                RefreshToken(refresh).blacklist()
            except (AttributeError, TokenError):
                pass

        response = Response({'detail': _('Logged out')})
        delete_auth_cookies(response)
        return response


@method_decorator(ensure_csrf_cookie, name='dispatch')
class CSRFTokenView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        token = get_token(request)
        return Response({'detail': _('CSRF cookie set'), 'csrfToken': token})


class EmailVerifyView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get_serializer_data(self, request):
        if request.method == 'GET':
            return request.query_params
        return request.data

    def get(self, request):
        return self.post(request)

    def post(self, request):
        serializer = EmailVerificationSerializer(data=self.get_serializer_data(request))
        serializer.is_valid(raise_exception=True)
        return Response({'detail': _('Email verified.')})


class EmailResendView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = EmailResendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': _('If an unverified account exists, a verification email has been sent.')})


class PasswordResetView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': _('If an account exists for this email, a reset email has been sent.')})


class PasswordResetConfirmView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': _('Password reset complete.')})


class ChangePasswordView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': _('Password changed.')})


class ProfileView(APIView):
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def get(self, request):
        return Response(UserSerializer(request.user, context={'request': request}).data)

    def patch(self, request):
        serializer = UpdateProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user, context={'request': request}).data)

    def delete(self, request):
        serializer = DeleteAccountSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator(csrf_protect, name='dispatch')
class GoogleLoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = GoogleLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = Response({'detail': _('Login successful')})
        set_auth_cookies(
            response,
            serializer.validated_data['access'],
            serializer.validated_data['refresh'],
        )
        return response


class PublicUserProfileView(generics.RetrieveAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = PublicUserSerializer
    permission_classes = (permissions.AllowAny,)
    lookup_field = 'username'
    lookup_url_kwarg = 'username'


class UserStatusViewSet(viewsets.ModelViewSet):
    serializer_class = UserStatusSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')

    def get_queryset(self):
        return UserStatus.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CurrentStatusView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = CurrentStatusSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.current_status_id = serializer.validated_data.get('status_id')
        request.user.save(update_fields=('current_status',))
        return Response(UserSerializer(request.user, context={'request': request}).data)

    def delete(self, request):
        request.user.current_status = None
        request.user.save(update_fields=('current_status',))
        return Response(status=status.HTTP_204_NO_CONTENT)


class FriendListView(generics.ListCreateAPIView):
    serializer_class = FriendSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Friend.objects.filter(user=self.request.user, status=Friend.Status.ACCEPTED).select_related('friend')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FriendDetailView(generics.DestroyAPIView):
    serializer_class = FriendSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'friend_id'

    def get_queryset(self):
        return Friend.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        friend_id = kwargs.get('friend_id')
        try:
            friend = Friend.objects.get(user=request.user, friend_id=friend_id)
            friend.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Friend.DoesNotExist:
            return Response({'detail': _('Friend not found.')}, status=status.HTTP_404_NOT_FOUND)


class FriendRequestListView(generics.ListAPIView):
    serializer_class = FriendSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Friend.objects.filter(friend=self.request.user, status=Friend.Status.PENDING).select_related('user')


class AcceptFriendRequestView(generics.UpdateAPIView):
    serializer_class = FriendSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'request_id'

    def get_queryset(self):
        return Friend.objects.filter(friend=self.request.user, status=Friend.Status.PENDING)

    def update(self, request, *args, **kwargs):
        request_id = kwargs.get('request_id')
        try:
            friend_request = Friend.objects.get(pk=request_id, friend=request.user, status=Friend.Status.PENDING)
            friend_request.status = Friend.Status.ACCEPTED
            friend_request.save()
            # Create reciprocal friendship
            Friend.objects.create(
                user=request.user,
                friend=friend_request.user,
                status=Friend.Status.ACCEPTED
            )
            return Response(FriendSerializer(friend_request).data)
        except Friend.DoesNotExist:
            return Response({'detail': _('Friend request not found.')}, status=status.HTTP_404_NOT_FOUND)


class RejectFriendRequestView(generics.UpdateAPIView):
    serializer_class = FriendSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'request_id'

    def get_queryset(self):
        return Friend.objects.filter(friend=self.request.user, status=Friend.Status.PENDING)

    def update(self, request, *args, **kwargs):
        request_id = kwargs.get('request_id')
        try:
            friend_request = Friend.objects.get(pk=request_id, friend=request.user, status=Friend.Status.PENDING)
            friend_request.status = Friend.Status.REJECTED
            friend_request.save()
            return Response(FriendSerializer(friend_request).data)
        except Friend.DoesNotExist:
            return Response({'detail': _('Friend request not found.')}, status=status.HTTP_404_NOT_FOUND)


class FriendStatusView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, user_id):
        friend = Friend.objects.filter(user=request.user, friend_id=user_id).first()
        if friend:
            return Response({
                'is_friend': friend.status == Friend.Status.ACCEPTED,
                'status': friend.status
            })
        return Response({'is_friend': False, 'status': None})
