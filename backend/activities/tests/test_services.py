from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from activities.models import ActivityRole, JoinRequest, Participant, PermissionCode
from activities.selectors import get_activities_for_user
from activities.services import (
    approve_join_request,
    assign_participant_role,
    create_activity,
    join_activity,
    reject_join_request,
    remove_participant,
    update_activity,
)


class ActivityRoleBehaviorTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user('owner', email='owner@example.com', password='pass')
        self.member = get_user_model().objects.create_user('member', email='member@example.com', password='pass')
        self.activity = create_activity(user=self.owner, title='Room')

    def test_new_activity_has_default_user_role_with_map_visibility(self):
        user_role = ActivityRole.objects.get(activity=self.activity, name='User')

        self.assertEqual(user_role.participants.count(), 0)
        grant = user_role.permission_grants.get(permission__code=PermissionCode.VIEW_PARTICIPANTS_MAP)
        self.assertEqual(grant.scope, {'visibility': 'everyone'})

    def test_join_assigns_default_user_role(self):
        join_req = join_activity(activity=self.activity, user=self.member)
        participant = approve_join_request(join_request=join_req)

        self.assertEqual(participant.role.name, 'User')

    def test_join_uses_selected_default_role(self):
        coordinator = ActivityRole.objects.create(activity=self.activity, name='Coordinator')
        update_activity(activity=self.activity, default_role=coordinator)

        join_req = join_activity(activity=self.activity, user=self.member)
        participant = approve_join_request(join_request=join_req)

        self.assertEqual(participant.role, coordinator)

    def test_owner_role_cannot_be_assigned_to_another_participant(self):
        join_req = join_activity(activity=self.activity, user=self.member)
        participant = approve_join_request(join_request=join_req)
        owner_role = ActivityRole.objects.get(activity=self.activity, name='Owner')

        with self.assertRaisesMessage(ValidationError, 'The Owner role can only belong to the activity owner.'):
            assign_participant_role(participant=participant, role=owner_role)

        self.assertEqual(Participant.objects.get(pk=participant.pk).role.name, 'User')

    def test_activity_list_counts_owner_and_members(self):
        join_req = join_activity(activity=self.activity, user=self.member)
        approve_join_request(join_request=join_req)

        listed_activity = get_activities_for_user(user=self.member).get(pk=self.activity.pk)

        self.assertEqual(listed_activity.participant_count, 2)

    def test_owner_can_remove_member(self):
        join_req = join_activity(activity=self.activity, user=self.member)
        participant = approve_join_request(join_request=join_req)

        remove_participant(participant=participant)

        self.assertFalse(Participant.objects.filter(pk=participant.pk).exists())

    def test_owner_cannot_be_removed(self):
        owner_participant = Participant.objects.get(activity=self.activity, user=self.owner)

        with self.assertRaisesMessage(ValidationError, 'The Activity Owner cannot be removed.'):
            remove_participant(participant=owner_participant)


class JoinRequestTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user('owner', email='owner@example.com', password='pass')
        self.member = get_user_model().objects.create_user('member', email='member@example.com', password='pass')
        self.activity = create_activity(user=self.owner, title='Room')

    def test_create_join_request(self):
        join_req = join_activity(activity=self.activity, user=self.member)
        self.assertEqual(join_req.status, JoinRequest.Status.PENDING)
        self.assertEqual(join_req.activity, self.activity)
        self.assertEqual(join_req.user, self.member)

    def test_approve_join_request(self):
        join_req = join_activity(activity=self.activity, user=self.member)
        participant = approve_join_request(join_request=join_req)
        self.assertEqual(Participant.objects.filter(activity=self.activity, user=self.member).count(), 1)
        join_req.refresh_from_db()
        self.assertEqual(join_req.status, JoinRequest.Status.ACCEPTED)

    def test_reject_join_request(self):
        join_req = join_activity(activity=self.activity, user=self.member)
        reject_join_request(join_request=join_req)
        self.assertEqual(Participant.objects.filter(activity=self.activity, user=self.member).count(), 0)
        join_req.refresh_from_db()
        self.assertEqual(join_req.status, JoinRequest.Status.REJECTED)
