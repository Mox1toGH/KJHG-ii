from datetime import timedelta
from typing import Any

from django.db import IntegrityError, transaction
from django.db.models import F
from django.utils import timezone

try:
    import h3
except ImportError:  # Keep Django checks/imports usable before dependencies are installed.
    h3 = None

from .config import H3_RESOLUTION
from .models import ScratchDiscovery
from .realtime import publish_cell_discovered, publish_statistics_updated


class ScratchMapService:
    """Application service for permanent, user-owned H3 discoveries."""

    @staticmethod
    def _cell_for_coordinates(latitude: float, longitude: float) -> str:
        if h3 is None:
            raise RuntimeError('The h3 package is required for Scratch Map discovery.')
        return h3.latlng_to_cell(latitude, longitude, H3_RESOLUTION)

    @staticmethod
    def discover_cell(*, user, latitude: float, longitude: float) -> tuple[ScratchDiscovery, bool]:
        h3_index = ScratchMapService._cell_for_coordinates(latitude, longitude)
        try:
            with transaction.atomic():
                discovery = ScratchDiscovery.objects.create(
                    user=user,
                    h3_index=h3_index,
                    latitude=latitude,
                    longitude=longitude,
                )
                # Increment hexagons_explored counter
                user.__class__.objects.filter(pk=user.pk).update(hexagons_explored=F('hexagons_explored') + 1)
        except IntegrityError:
            discovery = ScratchDiscovery.objects.get(user=user, h3_index=h3_index)
            return discovery, False

        transaction.on_commit(lambda: publish_cell_discovered(discovery))
        transaction.on_commit(
            lambda: publish_statistics_updated(user.id, ScratchMapService.statistics(user))
        )
        return discovery, True

    @staticmethod
    def discoveries(user):
        return ScratchDiscovery.objects.filter(user=user).only(
            'id', 'h3_index', 'discovered_at'
        )

    @staticmethod
    def statistics(user) -> dict[str, Any]:
        now = timezone.now()
        today = now.date()
        week_start = (now - timedelta(days=now.weekday())).date()
        month_start = now.replace(day=1).date()

        queryset = ScratchDiscovery.objects.filter(user=user)
        total = queryset.count()
        today_count = queryset.filter(discovered_at__date=today).count()
        weekly_count = queryset.filter(discovered_at__date__gte=week_start).count()
        monthly_count = queryset.filter(discovered_at__date__gte=month_start).count()

        explored_area = 0.0
        if h3 is not None and total:
            explored_area = total * h3.average_hexagon_area(H3_RESOLUTION, unit='km^2')

        return {
            'total_discovered_cells': total,
            'today_discoveries': today_count,
            'weekly_discoveries': weekly_count,
            'monthly_discoveries': monthly_count,
            'total_explored_area_km2': round(explored_area, 6),
        }
