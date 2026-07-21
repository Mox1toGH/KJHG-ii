from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory, force_authenticate

from activities.models import Activity, Participant
from tracking.models import ParticipantLocation
from tracking.services import update_participant_location
from tracking.views import ParticipantLocationListView

User = get_user_model()


class ParticipantLocationTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('owner', email='owner@example.com', password='pass')
        self.member = User.objects.create_user('member', email='member@example.com', password='pass')
        self.other = User.objects.create_user('other', email='other@example.com', password='pass')
        self.activity = Activity.objects.create(title='Room', created_by=self.owner)
        self.other_activity = Activity.objects.create(title='Other room', created_by=self.other)
        self.owner_participant = Participant.objects.create(activity=self.activity, user=self.owner)
        self.member_participant = Participant.objects.create(activity=self.activity, user=self.member)
        self.other_participant = Participant.objects.create(activity=self.other_activity, user=self.other)

    def test_location_is_created_then_updated_for_same_participant(self):
        first = update_participant_location(self.owner_participant, '50.4501', '30.5234', accuracy='4.5')
        second = update_participant_location(self.owner_participant, 50.4512, 30.5245)

        self.assertEqual(ParticipantLocation.objects.filter(participant=self.owner_participant).count(), 1)
        self.assertEqual(first.pk, second.pk)
        second.refresh_from_db()
        self.assertEqual(second.latitude, Decimal('50.451200'))
        self.assertEqual(second.longitude, Decimal('30.524500'))

    def test_invalid_coordinates_are_not_saved(self):
        with self.assertRaises(Exception):
            update_participant_location(self.owner_participant, 91, 30)
        self.assertFalse(ParticipantLocation.objects.exists())

    def test_activity_locations_endpoint_returns_all_members_and_numeric_coordinates(self):
        update_participant_location(self.owner_participant, 50.45, 30.52)
        request = APIRequestFactory().get(reverse('participant-locations', kwargs={'activity_id': self.activity.id}))
        force_authenticate(request, user=self.owner)
        response = ParticipantLocationListView.as_view()(request, activity_id=self.activity.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        owner_data = next(item for item in response.data if item['participant_id'] == str(self.owner_participant.id))
        member_data = next(item for item in response.data if item['participant_id'] == str(self.member_participant.id))
        self.assertIsInstance(owner_data['location']['latitude'], float)
        self.assertIsInstance(owner_data['location']['longitude'], float)
        self.assertIsNotNone(owner_data['last_updated'])
        self.assertIsNone(member_data['location'])

    def test_activity_locations_are_isolated(self):
        update_participant_location(self.other_participant, 49.84, 24.03)
        request = APIRequestFactory().get(reverse('participant-locations', kwargs={'activity_id': self.activity.id}))
        force_authenticate(request, user=self.owner)
        response = ParticipantLocationListView.as_view()(request, activity_id=self.activity.id)

        ids = {item['participant_id'] for item in response.data}
        self.assertNotIn(str(self.other_participant.id), ids)

    def test_participant_always_sees_own_location_without_map_permission(self):
        update_participant_location(self.member_participant, 50.46, 30.53)
        update_participant_location(self.owner_participant, 50.45, 30.52)
        request = APIRequestFactory().get(reverse('participant-locations', kwargs={'activity_id': self.activity.id}))
        force_authenticate(request, user=self.member)
        response = ParticipantLocationListView.as_view()(request, activity_id=self.activity.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual({item['participant_id'] for item in response.data}, {str(self.member_participant.id)})

    def test_anonymous_user_is_rejected_without_database_error(self):
        request = APIRequestFactory().get(reverse('participant-locations', kwargs={'activity_id': self.activity.id}))
        response = ParticipantLocationListView.as_view()(request, activity_id=self.activity.id)

        self.assertEqual(response.status_code, 401)
