from django.contrib import admin
from .models import Point

@admin.register(Point)
class PointAdmin(admin.ModelAdmin):
    # Відображення стовпчиків у списку
    list_display = ('user', 'room', 'points', 'created_at', 'updated_at')
    
    # Можливість клікнути на користувача або кімнату, щоб перейти в їх адмінку
    list_display_links = ('user', 'room')
    
    # Фільтри з правого боку
    list_filter = ('created_at', 'room')
    
    # Пошук за логіном користувача або ID (якщо потрібно)
    search_fields = ('user__username', 'user__email')
    
    # Поля, які не можна редагувати в адмінці
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    # Групування полів (якщо захочете додати більше)
    fieldsets = (
        (None, {
            'fields': ('id', 'user', 'room', 'points')
        }),
        ('Часові мітки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',) # Згортає цей блок за замовчуванням
        }),
    )