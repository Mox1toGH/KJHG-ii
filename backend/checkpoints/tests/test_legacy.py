from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from activities.models import Activity, ActivityPermission, ActivityRole, Participant, RolePermission
from checkpoints.models import Checkpoint, Route

User = get_user_model()


class CheckpointRoutePermissionTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('owner', email='owner@example.com', password='pass')
        self.member = User.objects.create_user('member', email='member@example.com', password='pass')
        self.activity = Activity.objects.create(title='Room', created_by=self.owner)
        Participant.objects.create(activity=self.activity, user=self.owner)
        role = ActivityRole.objects.create(activity=self.activity, name='Mapper')
        Participant.objects.create(activity=self.activity, user=self.member, role=role)
        checkpoint_permission = ActivityPermission.objects.get(code='checkpoints.create')
        RolePermission.objects.create(role=role, permission=checkpoint_permission)
        self.role = role
        self.client = APIClient()

    def checkpoint_payload(self):
        return {
            'activity': str(self.activity.id),
            'name': 'Start',
            'latitude': 50.45,
            'longitude': 30.52,
        }

    def route_payload(self, checkpoint_id):
        return {
            'activity': str(self.activity.id),
            'name': 'Morning route',
            'main_checkpoint': str(checkpoint_id),
            'points': [
                {'sequence_number': 1, 'latitude': 50.45, 'longitude': 30.52},
                {'sequence_number': 2, 'latitude': 50.46, 'longitude': 30.53},
                {'sequence_number': 3, 'latitude': 50.47, 'longitude': 30.54},
            ],
        }

    def test_checkpoint_permission_does_not_grant_route_creation(self):
        self.client.force_authenticate(self.member)
        checkpoint_response = self.client.post(
            '/api/checkpoints/checkpoints/', self.checkpoint_payload(), format='json'
        )
        self.assertEqual(checkpoint_response.status_code, 201)

        response = self.client.post(
            '/api/checkpoints/routes/',
            self.route_payload(checkpoint_response.data['id']),
            format='json',
        )
        self.assertEqual(response.status_code, 403)

    def test_route_permission_allows_author_crud_and_owner_can_manage_other_route(self):
        route_permission = ActivityPermission.objects.get(code='routes.create')
        RolePermission.objects.create(role=self.role, permission=route_permission)

        self.client.force_authenticate(self.member)
        checkpoint = Checkpoint.objects.create(
            activity=self.activity,
            created_by=self.member,
            name='Start',
            latitude=50.45,
            longitude=30.52,
        )
        response = self.client.post(
            '/api/checkpoints/routes/', self.route_payload(checkpoint.id), format='json'
        )
        self.assertEqual(response.status_code, 201)
        route_id = response.data['id']

        response = self.client.patch(
            f'/api/checkpoints/routes/{route_id}/', {'name': 'Updated route'}, format='json'
        )
        self.assertEqual(response.status_code, 200)

        self.client.force_authenticate(self.owner)
        response = self.client.patch(
            f'/api/checkpoints/routes/{route_id}/', {'name': 'Owner route'}, format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.delete(f'/api/checkpoints/routes/{route_id}/').status_code, 204)

        self.assertFalse(Route.objects.filter(pk=route_id).exists())
