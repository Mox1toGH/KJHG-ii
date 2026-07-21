import pytest
from rest_framework.test import APIClient

from tests.factories import ActivityFactory, ParticipantFactory, UserFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture(autouse=True)
def isolated_media_root(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path / 'media'


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def verified_user(db):
    return UserFactory(is_email_verified=True)


@pytest.fixture
def activity(db, user):
    return ActivityFactory(created_by=user)


@pytest.fixture
def participant(db, activity, user):
    return ParticipantFactory(activity=activity, user=user)


@pytest.fixture
def authenticated_client(api_client, verified_user):
    api_client.force_authenticate(verified_user)
    return api_client
