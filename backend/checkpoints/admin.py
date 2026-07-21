from django.contrib import admin
from .models import Checkpoint, Route, RoutePoint, Visit, CheckpointPhoto, RoutePointPhoto

# --- Inlines для фотографій ---
class CheckpointPhotoInline(admin.TabularInline):
    model = CheckpointPhoto
    extra = 1
    readonly_fields = ('created_at',)

class RoutePointPhotoInline(admin.TabularInline):
    model = RoutePointPhoto
    extra = 1
    readonly_fields = ('created_at',)

# --- Адмінки ---

@admin.register(Checkpoint)
class CheckpointAdmin(admin.ModelAdmin):
    list_display = ('name', 'activity', 'points', 'latitude', 'longitude', 'radius')
    list_filter = ('activity',)
    search_fields = ('name', 'activity__title')
    inlines = [CheckpointPhotoInline]

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'activity', 'main_checkpoint')
    search_fields = ('name',)

@admin.register(RoutePoint)
class RoutePointAdmin(admin.ModelAdmin):
    list_display = ('sequence_number', 'name', 'route', 'points', 'radius')
    list_filter = ('route',)
    ordering = ('route', 'sequence_number')
    inlines = [RoutePointPhotoInline]

@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('participant_username', 'point_name', 'visited_at', 'is_manual')
    list_filter = ('is_manual', 'visited_at')
    
    # Допоміжний метод для виводу імені учасника
    def participant_username(self, obj):
        return obj.participant.user.username
    participant_username.short_description = 'Participant'

    # Допоміжний метод для виводу назви точки (або чекпоїнт, або роут-поїнт)
    def point_name(self, obj):
        return obj.checkpoint.name if obj.checkpoint else obj.route_point.name
    point_name.short_description = 'Visited Point'

# Реєстрація окремих фото (якщо ви хочете керувати ними окремо)
@admin.register(CheckpointPhoto)
class CheckpointPhotoAdmin(admin.ModelAdmin):
    list_display = ('checkpoint', 'is_main', 'created_at')

@admin.register(RoutePointPhoto)
class RoutePointPhotoAdmin(admin.ModelAdmin):
    list_display = ('route_point', 'is_main', 'created_at')