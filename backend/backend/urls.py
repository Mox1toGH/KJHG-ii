
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path
from backend.views import FrontendIndexView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/activities/', include('activities.urls')),
    path('api/tracking/', include('tracking.urls')),
    path('api/locations/', include('locations.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/checkpoints/', include('checkpoints.urls')),
    path('api/points/', include('points.urls')),
    path('api/chat/', include('chat.urls')),
    path('api/homemap/', include('scratch_map.urls')),
    path('api/shop/', include('shop.urls')),
    # Serve frontend for all non-API routes (client-side routing)
    # This catch-all pattern must be last
    re_path(r'^(?!admin|api|media|static).*$', FrontendIndexView.as_view(), name='frontend-index'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
