import pytest
from django.test import RequestFactory
from rest_framework.request import Request

from accounts.backends import EmailOrUsernameBackend
from accounts.authentication import CookieJWTAuthentication
from tests.factories import UserFactory


@pytest.mark.django_db
@pytest.mark.parametrize('identifier', ['alice', 'ALICE@EXAMPLE.COM'])
def test_email_or_username_backend_authenticates_case_insensitively(identifier):
    user = UserFactory(username='alice', email='alice@example.com')
    assert EmailOrUsernameBackend().authenticate(None, username=identifier, password='StrongPass123!') == user


@pytest.mark.django_db
def test_email_or_username_backend_rejects_missing_or_wrong_credentials():
    UserFactory(username='alice', email='alice@example.com')
    backend = EmailOrUsernameBackend()
    assert backend.authenticate(None, username='alice', password='wrong') is None
    assert backend.authenticate(None, username=None, password=None) is None


def test_cookie_authentication_reads_access_cookie():
    request = Request(RequestFactory().get('/', HTTP_COOKIE='access_token=abc'))
    authentication = CookieJWTAuthentication()
    assert authentication.get_cookie_token(request) == 'abc'
