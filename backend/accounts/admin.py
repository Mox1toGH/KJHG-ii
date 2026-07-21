from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, UserStatus


@admin.register(UserStatus)
class UserStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at', 'updated_at')
    search_fields = ('name', 'user__username')


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            "Verification",
            {
                "fields": (
                    "is_email_verified",
                    "auth_provider",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "is_email_verified",
                    "auth_provider",
                ),
            },
        ),
    )

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_email_verified",
        "auth_provider",
        "is_staff",
    )

    list_filter = UserAdmin.list_filter + (
        "is_email_verified",
        "auth_provider",
    )
