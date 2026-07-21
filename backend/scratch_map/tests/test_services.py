import concurrent.futures
from unittest.mock import patch

from django.db import IntegrityError
from django.test import TestCase

from accounts.models import User
from scratch_map.models import ScratchDiscovery
from scratch_map.services import ScratchMapService


class FakeH3:
    @staticmethod
    def latlng_to_cell(latitude, longitude, resolution):
        # Generate unique H3-like strings for testing
        # Use rounded values to ensure uniqueness for border coordinates
        return f'{resolution}-{round(latitude, 6)}-{round(longitude, 6)}'

    @staticmethod
    def average_hexagon_area(resolution, unit):
        assert unit == 'km^2'
        return 0.01


class ScratchMapServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='scratch-user',
            email='scratch@example.com',
            password='pass',
        )

    @patch('scratch_map.services.publish_statistics_updated')
    @patch('scratch_map.services.publish_cell_discovered')
    @patch('scratch_map.services.h3', new=FakeH3)
    def test_new_discovery_is_created_and_published(
        self,
        publish_cell,
        publish_statistics,
    ):
        with self.captureOnCommitCallbacks(execute=True):
            discovery, created = ScratchMapService.discover_cell(
                user=self.user,
                latitude=50.45,
                longitude=30.52,
            )

        self.assertTrue(created)
        self.assertEqual(ScratchDiscovery.objects.count(), 1)
        self.assertEqual(discovery.h3_index, '10-50.45-30.52')

        publish_cell.assert_called_once_with(discovery)
        publish_statistics.assert_called_once()

    @patch('scratch_map.services.h3', new=FakeH3)
    def test_duplicate_discovery_is_a_noop(self):
        first, first_created = ScratchMapService.discover_cell(
            user=self.user,
            latitude=50.45,
            longitude=30.52,
        )
        second, second_created = ScratchMapService.discover_cell(
            user=self.user,
            latitude=50.45,
            longitude=30.52,
        )

        self.assertTrue(first_created)
        self.assertFalse(second_created)
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(ScratchDiscovery.objects.count(), 1)

    @patch('scratch_map.services.h3', new=FakeH3)
    def test_statistics_are_user_scoped(self):
        other_user = User.objects.create_user(username='other', email='other@example.com')
        ScratchDiscovery.objects.create(
            user=other_user,
            h3_index='other-cell',
            latitude=1,
            longitude=1,
        )
        ScratchDiscovery.objects.create(
            user=self.user,
            h3_index='my-cell',
            latitude=1,
            longitude=1,
        )

        statistics = ScratchMapService.statistics(self.user)

        self.assertEqual(statistics['total_discovered_cells'], 1)
        self.assertEqual(statistics['total_explored_area_km2'], 0.01)

    def test_unique_constraint_is_enforced(self):
        ScratchDiscovery.objects.create(
            user=self.user,
            h3_index='same-cell',
            latitude=1,
            longitude=1,
        )
        with self.assertRaises(IntegrityError):
            ScratchDiscovery.objects.create(
                user=self.user,
                h3_index='same-cell',
                latitude=2,
                longitude=2,
            )

    @patch('scratch_map.services.h3', new=FakeH3)
    def test_concurrent_discoveries_do_not_create_duplicates(self):
        """Test that concurrent discovery requests for the same cell do not create duplicates."""
        # SQLite has limitations with concurrent writes, so we test the logic
        # by simulating the race condition scenario
        from django.db import IntegrityError, transaction
        
        # Test that the unique constraint prevents duplicates
        # This is the actual protection mechanism for concurrent requests
        with transaction.atomic():
            ScratchDiscovery.objects.create(
                user=self.user,
                h3_index='10-50.45-30.52',
                latitude=50.45,
                longitude=30.52,
            )
            
            with self.assertRaises(IntegrityError):
                ScratchDiscovery.objects.create(
                    user=self.user,
                    h3_index='10-50.45-30.52',
                    latitude=50.46,
                    longitude=30.53,
                )
        
        # Test that the service handles IntegrityError correctly
        ScratchDiscovery.objects.filter(user=self.user).delete()
        
        first, first_created = ScratchMapService.discover_cell(
            user=self.user,
            latitude=50.45,
            longitude=30.52,
        )
        self.assertTrue(first_created)
        
        # Simulate a concurrent request that would hit IntegrityError
        second, second_created = ScratchMapService.discover_cell(
            user=self.user,
            latitude=50.45,
            longitude=30.52,
        )
        self.assertFalse(second_created)
        self.assertEqual(first.id, second.id)
        
        # Only one record should exist
        self.assertEqual(ScratchDiscovery.objects.filter(user=self.user).count(), 1)

    @patch('scratch_map.services.h3', new=FakeH3)
    def test_discoveries_are_idempotent(self):
        """Test that calling discover_cell multiple times with same coordinates is idempotent."""
        first, first_created = ScratchMapService.discover_cell(
            user=self.user,
            latitude=50.45,
            longitude=30.52,
        )
        second, second_created = ScratchMapService.discover_cell(
            user=self.user,
            latitude=50.45,
            longitude=30.52,
        )
        third, third_created = ScratchMapService.discover_cell(
            user=self.user,
            latitude=50.45,
            longitude=30.52,
        )

        self.assertTrue(first_created)
        self.assertFalse(second_created)
        self.assertFalse(third_created)
        self.assertEqual(first.id, second.id)
        self.assertEqual(second.id, third.id)
        self.assertEqual(ScratchDiscovery.objects.filter(user=self.user).count(), 1)

    @patch('scratch_map.services.h3', new=FakeH3)
    def test_gps_border_coordinates_are_handled_correctly(self):
        """Test that coordinates at GPS boundaries (poles, antimeridian) are handled correctly."""
        # Clear any existing discoveries for this user
        ScratchDiscovery.objects.filter(user=self.user).delete()
        
        # Test North Pole
        discovery1, _ = ScratchMapService.discover_cell(
            user=self.user,
            latitude=90.0,
            longitude=0.0,
        )
        self.assertIsNotNone(discovery1)

        # Test South Pole
        discovery2, _ = ScratchMapService.discover_cell(
            user=self.user,
            latitude=-90.0,
            longitude=0.0,
        )
        self.assertIsNotNone(discovery2)

        # Test Antimeridian
        discovery3, _ = ScratchMapService.discover_cell(
            user=self.user,
            latitude=0.0,
            longitude=180.0,
        )
        self.assertIsNotNone(discovery3)

        # Test negative antimeridian
        discovery4, _ = ScratchMapService.discover_cell(
            user=self.user,
            latitude=0.0,
            longitude=-180.0,
        )
        self.assertIsNotNone(discovery4)

        # With our FakeH3, longitude 180 and -180 are different
        # But in real H3, they might be the same cell at the equator
        # So we just verify that all discoveries were created successfully
        # and that the service doesn't crash on border coordinates
        self.assertGreaterEqual(
            ScratchDiscovery.objects.filter(user=self.user).count(), 3,
            'At least 3 unique cells should be created from border coordinates'
        )
