import pytest

from points.serializers import PointSerializer
from tests.factories import PointFactory, UserFactory


@pytest.mark.django_db
def test_point_serializer_exposes_read_only_fields_and_display_name():
    user = UserFactory(first_name='Ada', last_name='Lovelace')
    point = PointFactory(user=user)
    data = PointSerializer(point).data
    assert data['display_name'] == 'Ada Lovelace'
    assert set(PointSerializer().get_fields()['points'].read_only for _ in [0]) == {True}


@pytest.mark.django_db
def test_point_serializer_falls_back_to_username():
    user = UserFactory(first_name='', last_name='')
    point = PointFactory(user=user)
    assert PointSerializer(point).data['display_name'] == user.username
