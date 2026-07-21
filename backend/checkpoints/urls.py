from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CheckpointViewSet, RouteViewSet, CheckInView, VisitViewSet, RoutePointViewSet,
    CheckpointQRCodeCollectionView, CheckpointQRCodeDeleteView, CheckpointQRCodeImageView,
    CheckpointQRCodesPDFView, CheckpointQRCodeScanView,
)

router = DefaultRouter()
router.register(r'checkpoints', CheckpointViewSet, basename='checkpoint')
router.register(r'routes', RouteViewSet, basename='route')
router.register(r'route-points', RoutePointViewSet, basename='routepoint')
router.register(r'visits', VisitViewSet, basename='visit')

urlpatterns = [
    path('', include(router.urls)),
    path('check-in/', CheckInView.as_view(), name='check-in'),
    path('checkpoints/<uuid:checkpoint_id>/qrcodes/', CheckpointQRCodeCollectionView.as_view(), name='checkpoint-qrcodes'),
    path('qrcodes/<uuid:pk>/', CheckpointQRCodeDeleteView.as_view(), name='checkpoint-qrcode-delete'),
    path('qrcodes/<uuid:pk>/image/', CheckpointQRCodeImageView.as_view(), name='checkpoint-qrcode-image'),
    path('checkpoints/<uuid:checkpoint_id>/qrcodes/pdf/', CheckpointQRCodesPDFView.as_view(), name='checkpoint-qrcodes-pdf'),
    path('qrcodes/scan/', CheckpointQRCodeScanView.as_view(), name='checkpoint-qrcode-scan'),
]
