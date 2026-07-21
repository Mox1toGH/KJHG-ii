from django.contrib import admin
from .models import ShopItem, AvatarItem, BadgeItem, UserItem


@admin.register(ShopItem)
class ShopItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'item_type', 'activity', 'price', 'created_at']
    list_filter = ['item_type', 'activity']
    search_fields = ['activity__title']


@admin.register(AvatarItem)
class AvatarItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'shop_item', 'icon_file']


@admin.register(BadgeItem)
class BadgeItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'shop_item', 'text', 'color']


@admin.register(UserItem)
class UserItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'shop_item', 'is_equipped', 'purchased_at']
    list_filter = ['is_equipped', 'shop_item__item_type']
