from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ChangePasswordView,
    CSRFTokenView,
    EmailResendView,
    EmailVerifyView,
    GoogleLoginView,
    LoginView,
    LogoutView,
    ProfileView,
    PublicUserProfileView,
    PasswordResetConfirmView,
    PasswordResetView,
    RefreshView,
    RegisterView,
    CurrentStatusView,
    UserStatusViewSet,
    FriendListView,
    FriendDetailView,
    FriendStatusView,
    FriendRequestListView,
    AcceptFriendRequestView,
    RejectFriendRequestView,
)


app_name = 'accounts'

router = DefaultRouter()
router.register(r'statuses', UserStatusViewSet, basename='status')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('csrf/', CSRFTokenView.as_view(), name='csrf'),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', RefreshView.as_view(), name='refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('email/verify/', EmailVerifyView.as_view(), name='email-verify'),
    path('email/resend/', EmailResendView.as_view(), name='email-resend'),
    path('password/reset/', PasswordResetView.as_view(), name='password-reset'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('password/change/', ChangePasswordView.as_view(), name='password-change'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('status/current/', CurrentStatusView.as_view(), name='current-status'),
    path('google/', GoogleLoginView.as_view(), name='google-login'),
    path('friends/', FriendListView.as_view(), name='friends'),
    path('friends/<int:friend_id>/', FriendDetailView.as_view(), name='friend-detail'),
    path('friends/status/<int:user_id>/', FriendStatusView.as_view(), name='friend-status'),
    path('friends/requests/', FriendRequestListView.as_view(), name='friend-requests'),
    path('friends/requests/<int:request_id>/accept/', AcceptFriendRequestView.as_view(), name='accept-friend-request'),
    path('friends/requests/<int:request_id>/reject/', RejectFriendRequestView.as_view(), name='reject-friend-request'),
    path('<str:username>/', PublicUserProfileView.as_view(), name='public-profile'),
]
