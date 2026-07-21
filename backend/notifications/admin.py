from django.contrib import admin

from .models import Notification, UserNotificationPreferences


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'type', 'is_read', 'created_at', 'deleted_at')
    list_filter = ('type', 'read_at', 'deleted_at')
    search_fields = ('title', 'body', 'user__username', 'user__email')
    readonly_fields = ('id', 'created_at', 'read_at', 'deleted_at')


@admin.register(UserNotificationPreferences)
class UserNotificationPreferencesAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_enabled', 'in_app_enabled')
    list_filter = ('email_enabled', 'in_app_enabled')
    search_fields = ('user__username', 'user__email')
