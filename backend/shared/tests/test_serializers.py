import pytest
from shared.serializers import MapObjectCreatorSerializer, CreatedBySerializerMixin
from tests.factories import UserFactory


@pytest.mark.django_db
class TestMapObjectCreatorSerializer:
    def test_serializer_fields(self):
        user = UserFactory(
            username='testuser',
            first_name='John',
            last_name='Doe',
            email='john@example.com'
        )
        serializer = MapObjectCreatorSerializer(user)
        data = serializer.data
        assert set(data.keys()) == {'id', 'username', 'display_name', 'avatar', 'current_status'}
        assert data['username'] == 'testuser'
        assert data['display_name'] == 'John Doe'

    def test_display_name_with_first_and_last_name(self):
        user = UserFactory(
            username='testuser',
            first_name='John',
            last_name='Doe'
        )
        serializer = MapObjectCreatorSerializer(user)
        assert serializer.data['display_name'] == 'John Doe'

    def test_display_name_with_first_name_only(self):
        user = UserFactory(
            username='testuser',
            first_name='John',
            last_name=''
        )
        serializer = MapObjectCreatorSerializer(user)
        assert serializer.data['display_name'] == 'John'

    def test_display_name_with_last_name_only(self):
        user = UserFactory(
            username='testuser',
            first_name='',
            last_name='Doe'
        )
        serializer = MapObjectCreatorSerializer(user)
        assert serializer.data['display_name'] == 'Doe'

    def test_display_name_without_names(self):
        user = UserFactory(
            username='testuser',
            first_name='',
            last_name=''
        )
        serializer = MapObjectCreatorSerializer(user)
        assert serializer.data['display_name'] == 'testuser'

    def test_display_name_with_whitespace(self):
        user = UserFactory(
            username='testuser',
            first_name='  John  ',
            last_name='  Doe  '
        )
        serializer = MapObjectCreatorSerializer(user)
        # The actual implementation concatenates with space then strips
        assert serializer.data['display_name'] == 'John     Doe'

    def test_current_status_when_set(self):
        from accounts.models import UserStatus
        user = UserFactory(username='testuser')
        status = UserStatus.objects.create(user=user, name='Working')
        user.current_status = status
        user.save()
        
        serializer = MapObjectCreatorSerializer(user)
        assert serializer.data['current_status'] == 'Working'

    def test_current_status_when_none(self):
        user = UserFactory(username='testuser')
        serializer = MapObjectCreatorSerializer(user)
        assert serializer.data['current_status'] is None


@pytest.mark.django_db
class TestCreatedBySerializerMixin:
    def test_get_creator_user_from_created_by(self):
        from rest_framework import serializers
        
        class TestSerializer(CreatedBySerializerMixin, serializers.Serializer):
            pass
        
        class TestModel:
            def __init__(self, created_by):
                self.created_by = created_by
        
        user = UserFactory(username='creator')
        instance = TestModel(created_by=user)
        serializer = TestSerializer()
        assert serializer.get_creator_user(instance) == user

    def test_get_creator_user_from_marker(self):
        from rest_framework import serializers
        
        class TestSerializer(CreatedBySerializerMixin, serializers.Serializer):
            pass
        
        class Marker:
            def __init__(self, created_by):
                self.created_by = created_by
        
        class TestModel:
            def __init__(self, marker):
                self.marker = marker
                self.created_by = None
        
        user = UserFactory(username='creator')
        marker = Marker(created_by=user)
        instance = TestModel(marker=marker)
        serializer = TestSerializer()
        assert serializer.get_creator_user(instance) == user

    def test_get_creator_user_from_route(self):
        from rest_framework import serializers
        
        class TestSerializer(CreatedBySerializerMixin, serializers.Serializer):
            pass
        
        class Route:
            def __init__(self, created_by):
                self.created_by = created_by
        
        class TestModel:
            def __init__(self, route):
                self.route = route
                self.marker = None
                self.created_by = None
        
        user = UserFactory(username='creator')
        route = Route(created_by=user)
        instance = TestModel(route=route)
        serializer = TestSerializer()
        assert serializer.get_creator_user(instance) == user

    def test_get_creator_user_priority_order(self):
        from rest_framework import serializers
        
        class TestSerializer(CreatedBySerializerMixin, serializers.Serializer):
            pass
        
        class Route:
            def __init__(self, created_by):
                self.created_by = created_by
        
        class Marker:
            def __init__(self, created_by):
                self.created_by = created_by
        
        class TestModel:
            def __init__(self, created_by, marker, route):
                self.created_by = created_by
                self.marker = marker
                self.route = route
        
        user1 = UserFactory(username='user1')
        user2 = UserFactory(username='user2')
        user3 = UserFactory(username='user3')
        
        marker = Marker(created_by=user2)
        route = Route(created_by=user3)
        instance = TestModel(created_by=user1, marker=marker, route=route)
        serializer = TestSerializer()
        assert serializer.get_creator_user(instance) == user1

    def test_get_creator_user_when_none(self):
        from rest_framework import serializers
        
        class TestSerializer(CreatedBySerializerMixin, serializers.Serializer):
            pass
        
        class TestModel:
            created_by = None
            marker = None
            route = None
        
        instance = TestModel()
        serializer = TestSerializer()
        assert serializer.get_creator_user(instance) is None

    def test_add_creator_with_creator(self):
        from rest_framework import serializers
        
        class TestSerializer(CreatedBySerializerMixin, serializers.Serializer):
            pass
        
        user = UserFactory(username='creator')
        serializer = TestSerializer(context={'request': None})
        data = {'id': 1}
        instance = type('obj', (object,), {'created_by': user})()
        result = serializer.add_creator(data, instance)
        assert 'creator' in result
        assert result['creator']['username'] == 'creator'

    def test_add_creator_without_creator(self):
        from rest_framework import serializers
        
        class TestSerializer(CreatedBySerializerMixin, serializers.Serializer):
            pass
        
        serializer = TestSerializer(context={'request': None})
        data = {'id': 1}
        instance = type('obj', (object,), {'created_by': None, 'marker': None, 'route': None})()
        result = serializer.add_creator(data, instance)
        assert 'creator' in result
        assert result['creator'] is None

    def test_to_representation_calls_add_creator(self):
        from rest_framework import serializers
        
        class TestSerializer(CreatedBySerializerMixin, serializers.Serializer):
            id = serializers.IntegerField()
        
        user = UserFactory(username='creator')
        instance = type('obj', (object,), {'id': 1, 'created_by': user})()
        serializer = TestSerializer(instance)
        data = serializer.data
        assert 'creator' in data
        assert data['creator']['username'] == 'creator'
