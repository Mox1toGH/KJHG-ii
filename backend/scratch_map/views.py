from rest_framework import generics, status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .config import H3_RESOLUTION
from .serializers import (
    ScratchDiscoveryInputSerializer,
    ScratchDiscoverySerializer,
    ScratchMapConfigSerializer,
    ScratchMapStatisticsSerializer,
)
from .services import ScratchMapService


class ScratchDiscoveryPagination(LimitOffsetPagination):
    default_limit = 1000
    max_limit = 5000


class ScratchDiscoveryListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ScratchDiscoverySerializer
    pagination_class = ScratchDiscoveryPagination

    def get_queryset(self):
        return ScratchMapService.discoveries(self.request.user)


class ScratchMapStatisticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(ScratchMapStatisticsSerializer(ScratchMapService.statistics(request.user)).data)


class ScratchMapDiscoverView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ScratchDiscoveryInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        discovery, created = ScratchMapService.discover_cell(
            user=request.user,
            **serializer.validated_data,
        )
        return Response(
            {
                'discovery': ScratchDiscoverySerializer(discovery).data,
                'created': created,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class ScratchMapConfigView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(ScratchMapConfigSerializer({'h3_resolution': H3_RESOLUTION}).data)
