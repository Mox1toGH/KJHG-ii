import pytest
from django.core.exceptions import ValidationError
from shop.models import ShopItem, AvatarItem, BadgeItem, UserItem
from tests.factories import UserFactory, ActivityFactory, ParticipantFactory


@pytest.mark.django_db
class TestShopItem:
    def test_shop_item_creation(self):
        activity = ActivityFactory()
        shop_item = ShopItem.objects.create(
            item_type=ShopItem.ItemType.AVATAR,
            activity=activity,
            price=100
        )
        assert shop_item.item_type == ShopItem.ItemType.AVATAR
        assert shop_item.activity == activity
        assert shop_item.price == 100

    def test_shop_item_str_representation(self):
        activity = ActivityFactory(title='Test Activity')
        shop_item = ShopItem.objects.create(
            item_type=ShopItem.ItemType.BADGE,
            activity=activity,
            price=50
        )
        assert str(shop_item) == 'BADGE - Test Activity'

    def test_shop_item_ordering(self):
        activity = ActivityFactory()
        item1 = ShopItem.objects.create(
            item_type=ShopItem.ItemType.AVATAR,
            activity=activity,
            price=100
        )
        item2 = ShopItem.objects.create(
            item_type=ShopItem.ItemType.BADGE,
            activity=activity,
            price=50
        )
        items = list(ShopItem.objects.all())
        assert items[0] == item2
        assert items[1] == item1


@pytest.mark.django_db
class TestAvatarItem:
    def test_avatar_item_creation(self):
        activity = ActivityFactory()
        shop_item = ShopItem.objects.create(
            item_type=ShopItem.ItemType.AVATAR,
            activity=activity,
            price=100
        )
        avatar = AvatarItem.objects.create(
            shop_item=shop_item,
            icon_file='avatars/test.png'
        )
        assert avatar.shop_item == shop_item
        assert avatar.icon_file == 'avatars/test.png'

    def test_avatar_item_str_representation(self):
        activity = ActivityFactory()
        shop_item = ShopItem.objects.create(
            item_type=ShopItem.ItemType.AVATAR,
            activity=activity,
            price=100
        )
        avatar = AvatarItem.objects.create(shop_item=shop_item)
        assert str(avatar) == f'Avatar for {shop_item}'


@pytest.mark.django_db
class TestBadgeItem:
    def test_badge_item_creation(self):
        activity = ActivityFactory()
        shop_item = ShopItem.objects.create(
            item_type=ShopItem.ItemType.BADGE,
            activity=activity,
            price=50
        )
        badge = BadgeItem.objects.create(
            shop_item=shop_item,
            text='Test Badge',
            color='#FF0000'
        )
        assert badge.shop_item == shop_item
        assert badge.text == 'Test Badge'
        assert badge.color == '#FF0000'

    def test_badge_item_default_color(self):
        activity = ActivityFactory()
        shop_item = ShopItem.objects.create(
            item_type=ShopItem.ItemType.BADGE,
            activity=activity,
            price=50
        )
        badge = BadgeItem.objects.create(
            shop_item=shop_item,
            text='Test Badge'
        )
        assert badge.color == '#3B82F6'

    def test_badge_item_str_representation(self):
        activity = ActivityFactory()
        shop_item = ShopItem.objects.create(
            item_type=ShopItem.ItemType.BADGE,
            activity=activity,
            price=50
        )
        badge = BadgeItem.objects.create(
            shop_item=shop_item,
            text='Test Badge',
            color='#FF0000'
        )
        assert str(badge) == 'Badge: Test Badge (#FF0000)'


@pytest.mark.django_db
class TestUserItem:
    def test_user_item_creation(self):
        user = UserFactory()
        activity = ActivityFactory()
        shop_item = ShopItem.objects.create(
            item_type=ShopItem.ItemType.AVATAR,
            activity=activity,
            price=100
        )
        user_item = UserItem.objects.create(
            user=user,
            shop_item=shop_item,
            is_equipped=True
        )
        assert user_item.user == user
        assert user_item.shop_item == shop_item
        assert user_item.is_equipped is True

    def test_user_item_default_is_equipped(self):
        user = UserFactory()
        activity = ActivityFactory()
        shop_item = ShopItem.objects.create(
            item_type=ShopItem.ItemType.AVATAR,
            activity=activity,
            price=100
        )
        user_item = UserItem.objects.create(
            user=user,
            shop_item=shop_item
        )
        assert user_item.is_equipped is False

    def test_user_item_unique_constraint(self):
        user = UserFactory()
        activity = ActivityFactory()
        shop_item = ShopItem.objects.create(
            item_type=ShopItem.ItemType.AVATAR,
            activity=activity,
            price=100
        )
        UserItem.objects.create(user=user, shop_item=shop_item)
        
        with pytest.raises(ValidationError):
            duplicate = UserItem(user=user, shop_item=shop_item)
            duplicate.full_clean()

    def test_user_item_str_representation(self):
        user = UserFactory(username='testuser')
        activity = ActivityFactory()
        shop_item = ShopItem.objects.create(
            item_type=ShopItem.ItemType.AVATAR,
            activity=activity,
            price=100
        )
        user_item = UserItem.objects.create(
            user=user,
            shop_item=shop_item,
            is_equipped=True
        )
        assert str(user_item) == f'testuser - AVATAR (equipped: True)'
