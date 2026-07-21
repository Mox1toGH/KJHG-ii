import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from shop.models import ShopItem, AvatarItem, BadgeItem, UserItem
from points.models import Point
from tests.factories import UserFactory, ActivityFactory, ParticipantFactory


@pytest.mark.django_db
class TestShopItemViewSet:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def authenticated_client(self, api_client):
        user = UserFactory(is_email_verified=True)
        api_client.force_authenticate(user)
        return api_client, user

    def test_list_shop_items_as_participant(self, authenticated_client):
        client, user = authenticated_client
        activity = ActivityFactory(created_by=user)
        ParticipantFactory(activity=activity, user=user)
        
        shop_item = ShopItem.objects.create(
            item_type=ShopItem.ItemType.AVATAR,
            activity=activity,
            price=100
        )
        
        url = '/api/shop/items/'
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['id'] == str(shop_item.id)

    def test_list_shop_items_as_owner(self, authenticated_client):
        client, user = authenticated_client
        activity = ActivityFactory(created_by=user)
        
        shop_item = ShopItem.objects.create(
            item_type=ShopItem.ItemType.AVATAR,
            activity=activity,
            price=100
        )
        
        url = '/api/shop/items/'
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_list_shop_items_filters_by_activity(self, authenticated_client):
        client, user = authenticated_client
        activity1 = ActivityFactory(created_by=user)
        activity2 = ActivityFactory(created_by=user)
        
        ShopItem.objects.create(
            item_type=ShopItem.ItemType.AVATAR,
            activity=activity1,
            price=100
        )
        ShopItem.objects.create(
            item_type=ShopItem.ItemType.BADGE,
            activity=activity2,
            price=50
        )
        
        url = f'/api/shop/items/?activity_id={activity1.id}'
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['activity'] == activity1.id

    def test_list_shop_items_unauthorized(self, api_client):
        url = '/api/shop/items/'
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_shop_item_as_owner(self, authenticated_client):
        from django.core.files.uploadedfile import SimpleUploadedFile
        client, user = authenticated_client
        activity = ActivityFactory(created_by=user)
        
        url = '/api/shop/items/'
        icon_file = SimpleUploadedFile(
            "test.png", b"file_content", content_type="image/png"
        )
        data = {
            'item_type': ShopItem.ItemType.AVATAR,
            'activity': activity.id,
            'price': 100,
            'icon_file': icon_file
        }
        response = client.post(url, data, format='multipart')
        assert response.status_code == status.HTTP_201_CREATED
        assert ShopItem.objects.count() == 1

    def test_create_shop_item_as_non_owner_fails(self, authenticated_client):
        from django.core.files.uploadedfile import SimpleUploadedFile
        client, user = authenticated_client
        other_user = UserFactory()
        activity = ActivityFactory(created_by=other_user)
        
        url = '/api/shop/items/'
        icon_file = SimpleUploadedFile(
            "test.png", b"file_content", content_type="image/png"
        )
        data = {
            'item_type': ShopItem.ItemType.AVATAR,
            'activity': activity.id,
            'price': 100,
            'icon_file': icon_file
        }
        response = client.post(url, data, format='multipart')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_retrieve_shop_item(self, authenticated_client):
        client, user = authenticated_client
        activity = ActivityFactory(created_by=user)
        shop_item = ShopItem.objects.create(
            item_type=ShopItem.ItemType.AVATAR,
            activity=activity,
            price=100
        )
        
        url = f'/api/shop/items/{shop_item.id}/'
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == str(shop_item.id)

    def test_update_shop_item(self, authenticated_client):
        client, user = authenticated_client
        activity = ActivityFactory(created_by=user)
        shop_item = ShopItem.objects.create(
            item_type=ShopItem.ItemType.AVATAR,
            activity=activity,
            price=100
        )
        
        url = f'/api/shop/items/{shop_item.id}/'
        data = {'price': 150}
        response = client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        shop_item.refresh_from_db()
        assert shop_item.price == 150

    def test_delete_shop_item(self, authenticated_client):
        client, user = authenticated_client
        activity = ActivityFactory(created_by=user)
        shop_item = ShopItem.objects.create(
            item_type=ShopItem.ItemType.AVATAR,
            activity=activity,
            price=100
        )
        
        url = f'/api/shop/items/{shop_item.id}/'
        response = client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert ShopItem.objects.count() == 0

    def test_purchase_item_success(self, authenticated_client):
        client, user = authenticated_client
        activity = ActivityFactory(created_by=user)
        shop_item = ShopItem.objects.create(
            item_type=ShopItem.ItemType.AVATAR,
            activity=activity,
            price=50
        )
        Point.objects.create(user=user, room=activity, points=100)
        
        url = '/api/shop/items/purchase/'
        data = {'shop_item_id': str(shop_item.id)}
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert UserItem.objects.count() == 1
        
        point = Point.objects.get(user=user, room=activity)
        assert point.points == 50

    def test_purchase_item_insufficient_points(self, authenticated_client):
        client, user = authenticated_client
        activity = ActivityFactory(created_by=user)
        shop_item = ShopItem.objects.create(
            item_type=ShopItem.ItemType.AVATAR,
            activity=activity,
            price=100
        )
        Point.objects.create(user=user, room=activity, points=50)
        
        url = '/api/shop/items/purchase/'
        data = {'shop_item_id': str(shop_item.id)}
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Not enough points' in response.data['error']

    def test_purchase_item_already_owned(self, authenticated_client):
        client, user = authenticated_client
        activity = ActivityFactory(created_by=user)
        shop_item = ShopItem.objects.create(
            item_type=ShopItem.ItemType.AVATAR,
            activity=activity,
            price=50
        )
        UserItem.objects.create(user=user, shop_item=shop_item)
        Point.objects.create(user=user, room=activity, points=100)
        
        url = '/api/shop/items/purchase/'
        data = {'shop_item_id': str(shop_item.id)}
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'already own' in response.data['error']

    def test_purchase_item_no_points(self, authenticated_client):
        client, user = authenticated_client
        activity = ActivityFactory(created_by=user)
        shop_item = ShopItem.objects.create(
            item_type=ShopItem.ItemType.AVATAR,
            activity=activity,
            price=50
        )
        
        url = '/api/shop/items/purchase/'
        data = {'shop_item_id': str(shop_item.id)}
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'no points' in response.data['error']

    def test_equip_item(self, authenticated_client):
        client, user = authenticated_client
        activity = ActivityFactory(created_by=user)
        shop_item = ShopItem.objects.create(
            item_type=ShopItem.ItemType.AVATAR,
            activity=activity,
            price=50
        )
        user_item = UserItem.objects.create(user=user, shop_item=shop_item)
        
        url = '/api/shop/items/equip/'
        data = {'user_item_id': str(user_item.id)}
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        user_item.refresh_from_db()
        assert user_item.is_equipped is True

    def test_unequip_item(self, authenticated_client):
        client, user = authenticated_client
        activity = ActivityFactory(created_by=user)
        shop_item = ShopItem.objects.create(
            item_type=ShopItem.ItemType.AVATAR,
            activity=activity,
            price=50
        )
        user_item = UserItem.objects.create(user=user, shop_item=shop_item, is_equipped=True)
        
        url = '/api/shop/items/equip/'
        data = {'user_item_id': str(user_item.id)}
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        user_item.refresh_from_db()
        assert user_item.is_equipped is False

    def test_equip_item_unequips_same_type(self, authenticated_client):
        client, user = authenticated_client
        activity = ActivityFactory(created_by=user)
        shop_item1 = ShopItem.objects.create(
            item_type=ShopItem.ItemType.AVATAR,
            activity=activity,
            price=50
        )
        shop_item2 = ShopItem.objects.create(
            item_type=ShopItem.ItemType.AVATAR,
            activity=activity,
            price=75
        )
        user_item1 = UserItem.objects.create(user=user, shop_item=shop_item1, is_equipped=True)
        user_item2 = UserItem.objects.create(user=user, shop_item=shop_item2, is_equipped=False)
        
        url = '/api/shop/items/equip/'
        data = {'user_item_id': str(user_item2.id)}
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        user_item1.refresh_from_db()
        user_item2.refresh_from_db()
        assert user_item1.is_equipped is False
        assert user_item2.is_equipped is True

    def test_equip_item_not_owned(self, authenticated_client):
        client, user = authenticated_client
        other_user = UserFactory()
        activity = ActivityFactory(created_by=user)
        shop_item = ShopItem.objects.create(
            item_type=ShopItem.ItemType.AVATAR,
            activity=activity,
            price=50
        )
        user_item = UserItem.objects.create(user=other_user, shop_item=shop_item)
        
        url = '/api/shop/items/equip/'
        data = {'user_item_id': str(user_item.id)}
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestUserItemViewSet:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def authenticated_client(self, api_client):
        user = UserFactory(is_email_verified=True)
        api_client.force_authenticate(user)
        return api_client, user

    def test_list_user_items(self, authenticated_client):
        client, user = authenticated_client
        activity = ActivityFactory(created_by=user)
        shop_item = ShopItem.objects.create(
            item_type=ShopItem.ItemType.AVATAR,
            activity=activity,
            price=50
        )
        UserItem.objects.create(user=user, shop_item=shop_item)
        
        url = '/api/shop/user-items/'
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_list_user_items_filters_by_user_id(self, authenticated_client):
        client, user = authenticated_client
        other_user = UserFactory()
        activity = ActivityFactory(created_by=user)
        shop_item = ShopItem.objects.create(
            item_type=ShopItem.ItemType.AVATAR,
            activity=activity,
            price=50
        )
        UserItem.objects.create(user=user, shop_item=shop_item)
        UserItem.objects.create(user=other_user, shop_item=shop_item)
        
        url = f'/api/shop/user-items/?user_id={other_user.id}'
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['user'] == other_user.id

    def test_list_user_items_filters_by_activity(self, authenticated_client):
        client, user = authenticated_client
        activity1 = ActivityFactory(created_by=user)
        activity2 = ActivityFactory(created_by=user)
        shop_item1 = ShopItem.objects.create(
            item_type=ShopItem.ItemType.AVATAR,
            activity=activity1,
            price=50
        )
        shop_item2 = ShopItem.objects.create(
            item_type=ShopItem.ItemType.BADGE,
            activity=activity2,
            price=50
        )
        UserItem.objects.create(user=user, shop_item=shop_item1)
        UserItem.objects.create(user=user, shop_item=shop_item2)
        
        url = f'/api/shop/user-items/?activity_id={activity1.id}'
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_list_user_items_filters_by_item_type(self, authenticated_client):
        client, user = authenticated_client
        activity = ActivityFactory(created_by=user)
        shop_item1 = ShopItem.objects.create(
            item_type=ShopItem.ItemType.AVATAR,
            activity=activity,
            price=50
        )
        shop_item2 = ShopItem.objects.create(
            item_type=ShopItem.ItemType.BADGE,
            activity=activity,
            price=50
        )
        UserItem.objects.create(user=user, shop_item=shop_item1)
        UserItem.objects.create(user=user, shop_item=shop_item2)
        
        url = '/api/shop/user-items/?item_type=AVATAR'
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_retrieve_user_item(self, authenticated_client):
        client, user = authenticated_client
        activity = ActivityFactory(created_by=user)
        shop_item = ShopItem.objects.create(
            item_type=ShopItem.ItemType.AVATAR,
            activity=activity,
            price=50
        )
        user_item = UserItem.objects.create(user=user, shop_item=shop_item)
        
        url = f'/api/shop/user-items/{user_item.id}/'
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == str(user_item.id)

    def test_list_user_items_unauthorized(self, api_client):
        url = '/api/shop/user-items/'
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
