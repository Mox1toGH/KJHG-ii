from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile

from activities.models import Activity, ActivityPermission, ActivityRole, Participant, RolePermission
from locations.models import ActivityZone, LocationMarker, MeetingPoint

User = get_user_model()

# Create your tests here.


class LocationPermissionTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('owner', email='owner@example.com', password='pass')
        self.member = User.objects.create_user('member', email='member@example.com', password='pass')
        self.activity = Activity.objects.create(title='Room', created_by=self.owner)
        self.owner_participant = Participant.objects.create(activity=self.activity, user=self.owner)
        self.role = ActivityRole.objects.create(activity=self.activity, name='Mapper')
        self.member_participant = Participant.objects.create(
            activity=self.activity, user=self.member, role=self.role
        )
        self.permission = ActivityPermission.objects.get(code='locations.create')
        RolePermission.objects.create(role=self.role, permission=self.permission)
        self.client = APIClient()

    def marker_payload(self):
        return {
            'activity': str(self.activity.id), 'name': 'Gate', 'color': '#F59E0B',
            'latitude': 50.45, 'longitude': 30.52,
        }

    def zone_payload(self):
        return {
            'activity': str(self.activity.id),
            'name': 'North Zone',
            'color': '#10B981',
            'points': [[30.52, 50.45], [30.53, 50.45], [30.53, 50.46]],
        }

    @staticmethod
    def image_upload():
        return SimpleUploadedFile(
            'gate.gif',
            b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff'
            b'!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00'
            b'\x02\x02D\x01\x00;',
            content_type='image/gif',
        )

    def test_role_grant_allows_creation_and_creator_can_delete(self):
        self.client.force_authenticate(self.member)
        response = self.client.post('/api/locations/markers/', self.marker_payload(), format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.client.delete(f"/api/locations/markers/{response.data['id']}/").status_code, 204)

    def test_member_without_grant_cannot_create_or_delete_another_users_marker(self):
        self.client.force_authenticate(self.owner)
        marker = LocationMarker.objects.create(
            activity=self.activity, created_by=self.owner, name='Gate', latitude=50, longitude=30
        )
        self.client.force_authenticate(self.member)
        self.role.permission_grants.all().delete()
        self.assertEqual(self.client.post('/api/locations/markers/', self.marker_payload(), format='json').status_code, 403)
        self.assertEqual(self.client.delete(f'/api/locations/markers/{marker.id}/').status_code, 403)

    def test_member_needs_photo_upload_grant(self):
        self.client.force_authenticate(self.owner)
        marker = LocationMarker.objects.create(
            activity=self.activity, created_by=self.owner, name='Gate', latitude=50, longitude=30
        )
        image = self.image_upload()

        self.client.force_authenticate(self.member)
        response = self.client.post(
            f'/api/locations/markers/{marker.id}/photos/', {'image': image}, format='multipart'
        )
        self.assertEqual(response.status_code, 403)

        upload_permission = ActivityPermission.objects.get(code='checkpoints.photos.upload')
        RolePermission.objects.create(role=self.role, permission=upload_permission)
        image = self.image_upload()
        response = self.client.post(
            f'/api/locations/markers/{marker.id}/photos/', {'image': image}, format='multipart'
        )
        self.assertEqual(response.status_code, 201)

    def test_owner_can_mark_existing_checkpoint_as_meeting_point(self):
        marker = LocationMarker.objects.create(
            activity=self.activity, created_by=self.owner, name='Gate', latitude=50, longitude=30
        )
        self.client.force_authenticate(self.owner)
        response = self.client.patch(
            f'/api/locations/markers/{marker.id}/',
            {'meeting_point': {'start_time': '18:00', 'end_time': '19:00'}},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['meeting_point'], {'start_time': '18:00', 'end_time': '19:00'})
        self.assertTrue(MeetingPoint.objects.filter(marker=marker).exists())

        response = self.client.patch(
            f'/api/locations/markers/{marker.id}/', {'meeting_point': None}, format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data['meeting_point'])

    def test_meeting_point_requires_end_after_start(self):
        marker = LocationMarker.objects.create(
            activity=self.activity, created_by=self.owner, name='Gate', latitude=50, longitude=30
        )
        self.client.force_authenticate(self.owner)
        response = self.client.patch(
            f'/api/locations/markers/{marker.id}/',
            {'meeting_point': {'start_time': '19:00', 'end_time': '18:00'}},
            format='json',
        )
        self.assertEqual(response.status_code, 400)

    def test_member_needs_meeting_point_permission(self):
        marker = LocationMarker.objects.create(
            activity=self.activity, created_by=self.member, name='Gate', latitude=50, longitude=30
        )
        self.client.force_authenticate(self.member)
        payload = {'meeting_point': {'start_time': '18:00', 'end_time': '19:00'}}

        response = self.client.patch(
            f'/api/locations/markers/{marker.id}/', payload, format='json'
        )
        self.assertEqual(response.status_code, 403)

        permission = ActivityPermission.objects.get(code='meeting_points.set')
        RolePermission.objects.create(role=self.role, permission=permission)
        response = self.client.patch(
            f'/api/locations/markers/{marker.id}/', payload, format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['meeting_point'], payload['meeting_point'])

    def test_unchanged_meeting_point_does_not_require_permission(self):
        marker = LocationMarker.objects.create(
            activity=self.activity, created_by=self.member, name='Gate', latitude=50, longitude=30
        )
        self.client.force_authenticate(self.member)
        response = self.client.patch(
            f'/api/locations/markers/{marker.id}/',
            {'name': 'Updated Gate', 'meeting_point': None},
            format='json',
        )
        self.assertEqual(response.status_code, 200)

    def test_role_grant_allows_zone_crud_for_creator(self):
        self.client.force_authenticate(self.member)
        response = self.client.post('/api/locations/zones/', self.zone_payload(), format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], 'North Zone')

        response = self.client.get('/api/locations/zones/', {'activity_id': str(self.activity.id)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        zone_id = response.data[0]['id']
        response = self.client.patch(
            f'/api/locations/zones/{zone_id}/',
            {'name': 'Renamed Zone', 'color': '#3B82F6'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Renamed Zone')
        self.assertEqual(response.data['color'], '#3B82F6')

        self.assertEqual(self.client.delete(f'/api/locations/zones/{zone_id}/').status_code, 204)

    def test_zone_requires_three_points_and_delete_permission(self):
        self.client.force_authenticate(self.member)
        response = self.client.post(
            '/api/locations/zones/',
            {**self.zone_payload(), 'points': [[30.52, 50.45], [30.53, 50.45]]},
            format='json',
        )
        self.assertEqual(response.status_code, 400)

        self.client.force_authenticate(self.owner)
        zone = ActivityZone.objects.create(
            activity=self.activity,
            created_by=self.owner,
            name='Owner Zone',
            points=[[30.52, 50.45], [30.53, 50.45], [30.53, 50.46]],
        )
        self.client.force_authenticate(self.member)
        self.assertEqual(self.client.delete(f'/api/locations/zones/{zone.id}/').status_code, 403)
