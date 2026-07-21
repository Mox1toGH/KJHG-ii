import pytest
from django.core.exceptions import ValidationError

from locations.models import ActivityZone, MeetingPoint
from tests.factories import ActivityZoneFactory, LocationMarkerFactory


@pytest.mark.django_db
def test_meeting_point_requires_end_after_start():
    marker = LocationMarkerFactory()
    meeting_point = MeetingPoint(marker=marker, start_time='18:00', end_time='17:00')

    with pytest.raises(ValidationError, match='End time must be after start time'):
        meeting_point.full_clean()


@pytest.mark.django_db
def test_location_photo_and_zone_factories_produce_valid_domain_objects():
    zone = ActivityZoneFactory(trigger_action=ActivityZone.TriggerAction.ON_ENTRY)
    assert len(zone.points) == 3
    assert str(zone) == f'{zone.name} in {zone.activity.title}'
