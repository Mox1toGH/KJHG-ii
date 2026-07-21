import pytest

from tests.factories import NotificationFactory, UserFactory


@pytest.mark.django_db
def test_notification_api_is_user_scoped_and_supports_preferences(api_client):
    user = UserFactory()
    other = UserFactory()
    NotificationFactory(user=user, title='Mine')
    NotificationFactory(user=other, title='Other')
    api_client.force_authenticate(user)

    response = api_client.get('/api/notifications/')
    assert response.status_code == 200
    assert [item['title'] for item in response.data] == ['Mine']

    response = api_client.get('/api/notifications/preferences/')
    assert response.status_code == 200
    response = api_client.put('/api/notifications/preferences/', {'email_enabled': True}, format='json')
    assert response.status_code == 200
    assert response.data['email_enabled'] is True


@pytest.mark.django_db
def test_notification_api_read_delete_and_clear(api_client):
    user = UserFactory()
    notification = NotificationFactory(user=user)
    api_client.force_authenticate(user)

    assert api_client.post(f'/api/notifications/{notification.pk}/read/').status_code == 200
    notification.refresh_from_db()
    assert notification.read_at is not None
    assert api_client.post('/api/notifications/read-all/').status_code == 200
    assert api_client.post('/api/notifications/clear/').status_code == 200
    notification.refresh_from_db()
    assert notification.deleted_at is not None
