from unittest.mock import patch

from django.test import TestCase

from activities.models import Activity, Participant
from accounts.models import User
from locations.models import LocationMarker, MeetingPoint


class MeetingPointNotificationTests(TestCase):
    def test_new_meeting_point_is_published_to_all_participants(self):
        owner = User.objects.create_user('owner', email='owner@example.com', password='pass')
        member = User.objects.create_user('member', email='member@example.com', password='pass')
        activity = Activity.objects.create(title='Hike', created_by=owner)
        Participant.objects.create(activity=activity, user=owner)
        Participant.objects.create(activity=activity, user=member)
        marker = LocationMarker.objects.create(
            activity=activity, created_by=owner, name='Gate', latitude=50, longitude=30,
        )

        with patch('notifications.services.async_to_sync') as async_to_sync:
            with self.captureOnCommitCallbacks(execute=True):
                MeetingPoint.objects.create(marker=marker, start_time='18:00', end_time='19:00')

        send = async_to_sync.return_value
        self.assertEqual(send.call_count, 2)
        groups = {call.args[0] for call in send.call_args_list}
        self.assertEqual(groups, {f'user_{owner.id}_notifications', f'user_{member.id}_notifications'})
        event = send.call_args_list[0].args[1]
        self.assertEqual(event['type'], 'notification.created')
        self.assertEqual(event['notification']['type'], 'meeting_point.created')
