from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from scratch_map.models import ScratchDiscovery


class ScratchMapApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='api-user',
            email='api@example.com',
            password='pass',
        )
        self.other_user = User.objects.create_user(
            username='api-other',
            email='api-other@example.com',
            password='pass',
        )
        self.client.force_authenticate(user=self.user)

    def test_discoveries_are_private(self):
        ScratchDiscovery.objects.create(
            user=self.user,
            h3_index='my-cell',
            latitude=1,
            longitude=1,
        )
        ScratchDiscovery.objects.create(
            user=self.other_user,
            h3_index='other-cell',
            latitude=2,
            longitude=2,
        )

        response = self.client.get('/api/homemap/discovered/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['h3_index'], 'my-cell')

    @patch('scratch_map.services.h3')
    def test_discover_endpoint_returns_created_flag(self, h3_module):
        h3_module.latlng_to_cell.return_value = 'new-cell'

        response = self.client.post(
            '/api/homemap/discover/',
            {'latitude': 50.45, 'longitude': 30.52},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['created'])
        self.assertEqual(ScratchDiscovery.objects.filter(user=self.user).count(), 1)

    def test_discover_validation(self):
        response = self.client.post(
            '/api/homemap/discover/',
            {'latitude': 100, 'longitude': 30},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_endpoints_require_authentication(self):
        self.client.logout()

        response = self.client.get('/api/homemap/statistics/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_serializer_includes_user_id(self):
        ScratchDiscovery.objects.create(
            user=self.user,
            h3_index='my-cell',
            latitude=1,
            longitude=1,
        )

        response = self.client.get('/api/homemap/discovered/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user_id', response.data['results'][0])
        self.assertEqual(response.data['results'][0]['user_id'], self.user.id)

    def test_user_cannot_access_other_users_discoveries(self):
        ScratchDiscovery.objects.create(
            user=self.other_user,
            h3_index='other-cell',
            latitude=1,
            longitude=1,
        )

        response = self.client.get('/api/homemap/discovered/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_user_cannot_discover_for_another_user(self):
        """Test that the discover endpoint always creates discoveries for the authenticated user."""
        with patch('scratch_map.services.h3') as h3_module:
            h3_module.latlng_to_cell.return_value = 'new-cell'

            response = self.client.post(
                '/api/homemap/discover/',
                {'latitude': 50.45, 'longitude': 30.52},
                format='json',
            )

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            
            # Verify the discovery belongs to the authenticated user
            discovery = ScratchDiscovery.objects.get(h3_index='new-cell')
            self.assertEqual(discovery.user, self.user)
            self.assertNotEqual(discovery.user, self.other_user)
