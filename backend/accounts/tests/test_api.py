from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.tokens import email_verification_token
from accounts.models import UserStatus


User = get_user_model()


class AccountsApiTests(APITestCase):
    def create_verified_user(self, **overrides):
        data = {
            'username': 'jane',
            'email': 'jane@example.com',
            'first_name': 'Jane',
            'password': 'StrongPass123!',
            'is_email_verified': True,
        }
        data.update(overrides)
        password = data.pop('password')
        user = User(**data)
        user.set_password(password)
        user.save()
        return user, password

    def test_registration_sends_verification_and_blocks_login_until_verified(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'john',
            'email': 'John@Example.com',
            'first_name': 'John',
            'password': 'StrongPass123!',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {'detail': 'Registration successful. Please verify your email address.'})
        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)
        self.assertNotIn('access_token', response.cookies)
        self.assertNotIn('refresh_token', response.cookies)
        user = User.objects.get(username='john')
        self.assertEqual(user.email, 'john@example.com')
        self.assertFalse(user.is_email_verified)
        self.assertEqual(user.auth_provider, User.AuthProvider.LOCAL)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(f'{settings.FRONTEND_URL}/email/verify?uid=', mail.outbox[0].body)
        self.assertIn('&token=', mail.outbox[0].body)

        login = self.client.post(reverse('accounts:login'), {
            'identifier': 'john',
            'password': 'StrongPass123!',
        }, format='json')
        self.assertEqual(login.status_code, status.HTTP_400_BAD_REQUEST)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = email_verification_token.make_token(user)
        verify = self.client.post(reverse('accounts:email-verify'), {'uid': uid, 'token': token}, format='json')
        self.assertEqual(verify.status_code, status.HTTP_200_OK)

        login = self.client.post(reverse('accounts:login'), {
            'identifier': 'john@example.com',
            'password': 'StrongPass123!',
        }, format='json')
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        self.assertEqual(login.data, {'detail': 'Login successful'})
        self.assertNotIn('access', login.data)
        self.assertNotIn('refresh', login.data)
        self.assertIn('access_token', login.cookies)
        self.assertIn('refresh_token', login.cookies)
        self.assertTrue(login.cookies['access_token']['httponly'])
        self.assertTrue(login.cookies['refresh_token']['httponly'])

        profile = self.client.get(reverse('accounts:profile'))
        self.assertEqual(profile.status_code, status.HTTP_200_OK)
        self.assertEqual(profile.data['username'], 'john')

        refresh = self.client.post(reverse('accounts:refresh'))
        self.assertEqual(refresh.status_code, status.HTTP_200_OK)
        self.assertEqual(refresh.data, {'detail': 'Token refreshed'})
        self.assertIn('access_token', refresh.cookies)

        logout = self.client.post(reverse('accounts:logout'))
        self.assertEqual(logout.status_code, status.HTTP_200_OK)
        self.assertEqual(logout.data, {'detail': 'Logged out'})
        self.assertEqual(logout.cookies['access_token'].value, '')
        self.assertEqual(logout.cookies['refresh_token'].value, '')

    def test_bearer_token_authentication_still_works(self):
        user, _ = self.create_verified_user()
        refresh = RefreshToken.for_user(user)

        response = self.client.get(
            reverse('accounts:profile'),
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], user.username)

    def test_public_profile_exposes_name_username_and_email(self):
        self.create_verified_user(username='publicuser', email='public@example.com')

        response = self.client.get(reverse('accounts:public-profile', kwargs={'username': 'publicuser'}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data), {'id', 'username', 'email', 'first_name', 'last_name', 'avatar', 'current_status', 'created_at', 'last_seen', 'hexagons_explored', 'checkpoints_visited'})
        self.assertEqual(response.data['email'], 'public@example.com')

    def test_new_users_receive_default_statuses(self):
        user, _ = self.create_verified_user()

        self.assertEqual(
            list(user.statuses.values_list('name', flat=True)),
            ['Вільний', 'Зайнятий', 'Free', 'Busy'],
        )

    def test_statuses_are_owned_and_current_status_can_be_cleared(self):
        user, _ = self.create_verified_user()
        other, _ = self.create_verified_user(username='other', email='other@example.com')
        user.avatar.name = 'avatars/jane.jpg'
        user.save(update_fields=('avatar',))
        self.client.force_authenticate(user)

        create = self.client.post(reverse('accounts:status-list'), {'name': 'Working'}, format='json')
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        working_id = create.data['id']

        listing = self.client.get(reverse('accounts:status-list'))
        self.assertEqual(listing.status_code, status.HTTP_200_OK)
        self.assertEqual({item['name'] for item in listing.data}, {'Вільний', 'Зайнятий', 'Working', 'Free', 'Busy'})

        select = self.client.post(reverse('accounts:current-status'), {'status_id': working_id}, format='json')
        self.assertEqual(select.status_code, status.HTTP_200_OK)
        self.assertEqual(select.data['current_status'], 'Working')
        self.assertEqual(select.data['avatar'], 'http://testserver/media/avatars/jane.jpg')

        forbidden = self.client.post(
            reverse('accounts:current-status'),
            {'status_id': other.statuses.first().id},
            format='json',
        )
        self.assertEqual(forbidden.status_code, status.HTTP_403_FORBIDDEN)

        deleted = self.client.delete(reverse('accounts:status-detail', kwargs={'pk': working_id}))
        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)
        user.refresh_from_db()
        self.assertIsNone(user.current_status)

    def test_change_password_requires_current_password(self):
        user, password = self.create_verified_user()
        self.client.force_authenticate(user)

        response = self.client.post(reverse('accounts:password-change'), {
            'current_password': password,
            'new_password': 'NewStrongPass123!',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.check_password('NewStrongPass123!'))

    def test_password_reset_confirm_changes_password_and_invalidates_old_token(self):
        user, _ = self.create_verified_user()
        RefreshToken.for_user(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        response = self.client.post(reverse('accounts:password-reset-confirm'), {
            'uid': uid,
            'token': token,
            'new_password': 'ResetStrongPass123!',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.check_password('ResetStrongPass123!'))
        self.assertFalse(default_token_generator.check_token(user, token))
        self.assertEqual(BlacklistedToken.objects.filter(token__user=user).count(), 1)

    def test_change_password_blacklists_existing_refresh_tokens(self):
        user, password = self.create_verified_user()
        RefreshToken.for_user(user)
        self.client.force_authenticate(user)

        response = self.client.post(reverse('accounts:password-change'), {
            'current_password': password,
            'new_password': 'NewStrongPass123!',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            BlacklistedToken.objects.filter(token__in=OutstandingToken.objects.filter(user=user)).count(),
            1,
        )

    def test_profile_email_change_requires_reverification(self):
        user, _ = self.create_verified_user()
        self.client.force_authenticate(user)

        response = self.client.patch(reverse('accounts:profile'), {'email': 'new@example.com'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.email, 'new@example.com')
        self.assertFalse(user.is_email_verified)
        self.assertEqual(len(mail.outbox), 1)

    def test_delete_account_requires_password(self):
        user, password = self.create_verified_user()
        self.client.force_authenticate(user)

        response = self.client.delete(reverse('accounts:profile'), {'password': password}, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(pk=user.pk).exists())

    @patch('accounts.services.GoogleAuthService.verify_id_token')
    def test_google_login_creates_verified_user_and_reuses_existing_email(self, verify_id_token):
        verify_id_token.return_value = {
            'email': 'google@example.com',
            'email_verified': True,
            'given_name': 'Gina',
        }

        first = self.client.post(reverse('accounts:google-login'), {'credential': 'token'}, format='json')
        second = self.client.post(reverse('accounts:google-login'), {'credential': 'token'}, format='json')

        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(first.data, {'detail': 'Login successful'})
        self.assertIn('access_token', first.cookies)
        self.assertIn('refresh_token', first.cookies)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(User.objects.filter(email='google@example.com').count(), 1)
        user = User.objects.get(email='google@example.com')
        self.assertTrue(user.is_email_verified)
        self.assertEqual(user.auth_provider, User.AuthProvider.GOOGLE)
