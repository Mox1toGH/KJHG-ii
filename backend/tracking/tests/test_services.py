from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError

from activities.models import ActivityRole, Participant
from tests.factories import ActivityFactory, ParticipantFactory, UserFactory
from tracking.models import ParticipantLocation
from tracking.services import set_participant_sos, update_participant_location


@pytest.mark.django_db
def test_location_update_validates_coordinates_and_optional_values():
    participant = ParticipantFactory()
    location = update_participant_location(participant, 50, 30, accuracy='4.5', heading=90, speed=2)
    assert location.latitude == 50
    assert location.accuracy == 4.5
    with pytest.raises(ValidationError, match='Latitude must be between'):
        update_participant_location(participant, 91, 30)
    with pytest.raises(ValidationError, match='Speed must be finite'):
        update_participant_location(participant, 50, 30, speed=float('inf'))


@pytest.mark.django_db
def test_location_update_is_idempotent_for_participant():
    participant = ParticipantFactory()
    first = update_participant_location(participant, 50, 30)
    second = update_participant_location(participant, 51, 31)
    assert first.pk == second.pk
    assert ParticipantLocation.objects.filter(participant=participant).count() == 1


@pytest.mark.django_db
def test_sos_state_is_idempotent_and_broadcasts_on_commit():
    participant = ParticipantFactory()
    with patch('tracking.services._broadcast_sos') as broadcast, patch(
        'tracking.services.publish_activity_notification'
    ) as notify:
        set_participant_sos(participant=participant, active=True)
        assert participant.sos_active is True
        notify.assert_called_once()
        set_participant_sos(participant=participant, active=True)
        assert notify.call_count == 1
    participant.refresh_from_db()
    assert participant.sos_active is True
