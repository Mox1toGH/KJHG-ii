import factory
from factory.django import DjangoModelFactory

from accounts.models import User
from activities.models import Activity, ActivityRole, Participant
from chat.models import ChatMessage
from checkpoints.models import Checkpoint, Route, RoutePoint
from locations.models import ActivityZone, LocationMarker
from notifications.models import Notification
from points.models import Point
from scratch_map.models import ScratchDiscovery
from shop.models import ShopItem, AvatarItem, BadgeItem, UserItem


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('email',)

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    first_name = factory.Faker('first_name')
    password = factory.PostGenerationMethodCall('set_password', 'StrongPass123!')
    is_email_verified = True


class ActivityFactory(DjangoModelFactory):
    class Meta:
        model = Activity

    title = factory.Sequence(lambda n: f'Activity {n}')
    created_by = factory.SubFactory(UserFactory)


class ActivityRoleFactory(DjangoModelFactory):
    class Meta:
        model = ActivityRole

    activity = factory.SubFactory(ActivityFactory)
    name = factory.Sequence(lambda n: f'Role {n}')


class ParticipantFactory(DjangoModelFactory):
    class Meta:
        model = Participant

    activity = factory.SubFactory(ActivityFactory)
    user = factory.SubFactory(UserFactory)
    role = None


class LocationMarkerFactory(DjangoModelFactory):
    class Meta:
        model = LocationMarker

    activity = factory.SubFactory(ActivityFactory)
    created_by = factory.SelfAttribute('activity.created_by')
    name = factory.Sequence(lambda n: f'Marker {n}')
    latitude = 50.4501
    longitude = 30.5234


class ActivityZoneFactory(DjangoModelFactory):
    class Meta:
        model = ActivityZone

    activity = factory.SubFactory(ActivityFactory)
    created_by = factory.SelfAttribute('activity.created_by')
    name = factory.Sequence(lambda n: f'Zone {n}')
    points = [[30.52, 50.45], [30.53, 50.45], [30.53, 50.46]]


class CheckpointFactory(DjangoModelFactory):
    class Meta:
        model = Checkpoint

    activity = factory.SubFactory(ActivityFactory)
    created_by = factory.SelfAttribute('activity.created_by')
    name = factory.Sequence(lambda n: f'Checkpoint {n}')
    latitude = 50.4501
    longitude = 30.5234


class RouteFactory(DjangoModelFactory):
    class Meta:
        model = Route

    activity = factory.SubFactory(ActivityFactory)
    created_by = factory.SelfAttribute('activity.created_by')
    main_checkpoint = factory.SubFactory(CheckpointFactory, activity=factory.SelfAttribute('..activity'))
    name = factory.Sequence(lambda n: f'Route {n}')


class RoutePointFactory(DjangoModelFactory):
    class Meta:
        model = RoutePoint

    route = factory.SubFactory(RouteFactory)
    sequence_number = factory.Sequence(lambda n: n + 1)
    latitude = 50.4501
    longitude = 30.5234


class ChatMessageFactory(DjangoModelFactory):
    class Meta:
        model = ChatMessage

    activity = factory.SubFactory(ActivityFactory)
    sender = factory.SubFactory(UserFactory)
    body = factory.Sequence(lambda n: f'Message {n}')


class NotificationFactory(DjangoModelFactory):
    class Meta:
        model = Notification

    user = factory.SubFactory(UserFactory)
    type = 'test.created'
    title = 'Test notification'
    body = 'Notification body'


class PointFactory(DjangoModelFactory):
    class Meta:
        model = Point

    user = factory.SubFactory(UserFactory)
    room = factory.SubFactory(ActivityFactory)
    points = 10


class ScratchDiscoveryFactory(DjangoModelFactory):
    class Meta:
        model = ScratchDiscovery

    user = factory.SubFactory(UserFactory)
    h3_index = factory.Sequence(lambda n: f'cell-{n}')
    latitude = 50.4501
    longitude = 30.5234


class ShopItemFactory(DjangoModelFactory):
    class Meta:
        model = ShopItem

    item_type = ShopItem.ItemType.AVATAR
    activity = factory.SubFactory(ActivityFactory)
    price = 100


class AvatarItemFactory(DjangoModelFactory):
    class Meta:
        model = AvatarItem

    shop_item = factory.SubFactory(ShopItemFactory, item_type=ShopItem.ItemType.AVATAR)
    icon_file = 'avatars/test.png'


class BadgeItemFactory(DjangoModelFactory):
    class Meta:
        model = BadgeItem

    shop_item = factory.SubFactory(ShopItemFactory, item_type=ShopItem.ItemType.BADGE)
    text = factory.Sequence(lambda n: f'Badge {n}')
    color = '#3B82F6'


class UserItemFactory(DjangoModelFactory):
    class Meta:
        model = UserItem

    user = factory.SubFactory(UserFactory)
    shop_item = factory.SubFactory(ShopItemFactory)
    is_equipped = False
