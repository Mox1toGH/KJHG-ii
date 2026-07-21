import uuid

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import resolve, reverse
from rest_framework import status
from rest_framework.test import APIClient

from activities.models import Participant
from activities.services import approve_join_request, create_activity, join_activity


class ActivityURLTests(SimpleTestCase):
    activity_id = uuid.UUID('11111111-1111-1111-1111-111111111111')
    role_id = uuid.UUID('22222222-2222-2222-2222-222222222222')

    def assert_route(self, name, expected_path, expected_actions, **kwargs):
        path = reverse(f'activities:{name}', kwargs=kwargs)
        self.assertEqual(path, expected_path)
        self.assertEqual(resolve(path).func.actions, expected_actions)

    def test_activity_list_route(self):
        self.assert_route(
            'activity-list',
            '/api/activities/',
            {'get': 'list', 'post': 'create'},
        )

    def test_activity_detail_route(self):
        self.assert_route(
            'activity-detail',
            f'/api/activities/{self.activity_id}/',
            {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'},
            pk=self.activity_id,
        )

    def test_activity_membership_routes(self):
        for name, action in [('activity-join', 'join'), ('activity-leave', 'leave')]:
            with self.subTest(name=name):
                self.assert_route(
                    name,
                    f'/api/activities/{self.activity_id}/{action}/',
                    {'post': action},
                    pk=self.activity_id,
                )

    def test_activity_role_list_route(self):
        self.assert_route(
            'activity-role-list',
            f'/api/activities/{self.activity_id}/roles/',
            {'get': 'list', 'post': 'create'},
            activity_pk=self.activity_id,
        )

    def test_activity_role_detail_route(self):
        self.assert_route(
            'activity-role-detail',
            f'/api/activities/{self.activity_id}/roles/{self.role_id}/',
            {'patch': 'partial_update', 'delete': 'destroy'},
            activity_pk=self.activity_id,
            pk=self.role_id,
        )

    def test_activity_participant_detail_route(self):
        self.assert_route(
            'activity-participant-detail',
            f'/api/activities/{self.activity_id}/participants/{self.role_id}/',
            {'patch': 'partial_update', 'delete': 'destroy'},
            activity_pk=self.activity_id,
            pk=self.role_id,
        )


class ActivityParticipantApiTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user('api-owner', email='api-owner@example.com', password='pass')
        self.member = get_user_model().objects.create_user('api-member', email='api-member@example.com', password='pass')
        self.activity = create_activity(user=self.owner, title='API room')
        join_req = join_activity(activity=self.activity, user=self.member)
        self.participant = approve_join_request(join_request=join_req)
        self.client = APIClient()

    def test_only_owner_can_remove_a_participant(self):
        self.client.force_authenticate(self.member)
        forbidden = self.client.delete(reverse('activities:activity-participant-detail', kwargs={
            'activity_pk': self.activity.pk,
            'pk': self.participant.pk,
        }))
        self.assertEqual(forbidden.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Participant.objects.filter(pk=self.participant.pk).exists())

        self.client.force_authenticate(self.owner)
        removed = self.client.delete(reverse('activities:activity-participant-detail', kwargs={
            'activity_pk': self.activity.pk,
            'pk': self.participant.pk,
        }))
        self.assertEqual(removed.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Participant.objects.filter(pk=self.participant.pk).exists())
