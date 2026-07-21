from rest_framework import serializers
from .models import ShopItem, AvatarItem, BadgeItem, UserItem


class AvatarItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvatarItem
        fields = ['id', 'icon_file']


class BadgeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BadgeItem
        fields = ['id', 'text', 'color']


class ShopItemSerializer(serializers.ModelSerializer):
    avatar = AvatarItemSerializer(read_only=True)
    badge = BadgeItemSerializer(read_only=True)

    class Meta:
        model = ShopItem
        fields = ['id', 'item_type', 'activity', 'price', 'created_at', 'updated_at', 'avatar', 'badge']


class ShopItemCreateSerializer(serializers.ModelSerializer):
    icon_file = serializers.FileField(required=False, allow_null=True)
    text = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    color = serializers.CharField(required=False, default='#3B82F6')

    class Meta:
        model = ShopItem
        fields = ['item_type', 'activity', 'price', 'icon_file', 'text', 'color']

    def validate(self, data):
        item_type = data.get('item_type')
        if item_type == ShopItem.ItemType.AVATAR:
            if not data.get('icon_file'):
                raise serializers.ValidationError("icon_file is required for avatar items")
        elif item_type == ShopItem.ItemType.BADGE:
            if not data.get('text'):
                raise serializers.ValidationError("text is required for badge items")
        return data

    def create(self, validated_data):
        icon_file = validated_data.pop('icon_file', None)
        text = validated_data.pop('text', None)
        color = validated_data.pop('color', '#3B82F6')

        shop_item = ShopItem.objects.create(**validated_data)

        if shop_item.item_type == ShopItem.ItemType.AVATAR:
            AvatarItem.objects.create(shop_item=shop_item, icon_file=icon_file)
        elif shop_item.item_type == ShopItem.ItemType.BADGE:
            BadgeItem.objects.create(shop_item=shop_item, text=text, color=color)

        return shop_item


class UserItemSerializer(serializers.ModelSerializer):
    shop_item = ShopItemSerializer(read_only=True)

    class Meta:
        model = UserItem
        fields = ['id', 'user', 'shop_item', 'is_equipped', 'purchased_at']
        read_only_fields = ['user', 'purchased_at']


class PurchaseItemSerializer(serializers.Serializer):
    shop_item_id = serializers.UUIDField()


class EquipItemSerializer(serializers.Serializer):
    user_item_id = serializers.UUIDField()
