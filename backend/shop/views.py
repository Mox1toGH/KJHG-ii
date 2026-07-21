from django.db.models import Q
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from points.models import Point
from .models import ShopItem, UserItem
from .serializers import (
    ShopItemSerializer,
    ShopItemCreateSerializer,
    UserItemSerializer,
    PurchaseItemSerializer,
    EquipItemSerializer,
)


class ShopItemViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return ShopItemCreateSerializer
        return ShopItemSerializer

    def get_queryset(self):
        queryset = ShopItem.objects.filter(
            Q(activity__participants__user=self.request.user) | Q(activity__created_by=self.request.user)
        ).select_related('activity').distinct()

        activity_id = self.request.query_params.get('activity_id')
        if activity_id:
            queryset = queryset.filter(activity_id=activity_id)

        return queryset

    def perform_create(self, serializer):
        activity = serializer.validated_data['activity']
        if activity.created_by != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Only the activity owner can create shop items')
        serializer.save()

    @action(detail=False, methods=['post'], url_path='purchase')
    def purchase(self, request):
        serializer = PurchaseItemSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        shop_item_id = serializer.validated_data['shop_item_id']
        try:
            shop_item = ShopItem.objects.get(id=shop_item_id)
        except ShopItem.DoesNotExist:
            return Response({'error': 'Shop item not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if user already owns this item
        if UserItem.objects.filter(user=request.user, shop_item=shop_item).exists():
            return Response({'error': 'You already own this item'}, status=status.HTTP_400_BAD_REQUEST)

        # Check user's points in the activity
        try:
            point = Point.objects.get(user=request.user, room=shop_item.activity)
        except Point.DoesNotExist:
            return Response({'error': 'You have no points in this activity'}, status=status.HTTP_400_BAD_REQUEST)

        if point.points < shop_item.price:
            return Response(
                {'error': f'Not enough points. You have {point.points}, need {shop_item.price}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Deduct points and create user item
        point.points -= shop_item.price
        point.save()

        user_item = UserItem.objects.create(user=request.user, shop_item=shop_item)

        return Response(UserItemSerializer(user_item).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='equip')
    def equip(self, request):
        serializer = EquipItemSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_item_id = serializer.validated_data['user_item_id']
        try:
            user_item = UserItem.objects.get(id=user_item_id, user=request.user)
        except UserItem.DoesNotExist:
            return Response({'error': 'User item not found'}, status=status.HTTP_404_NOT_FOUND)

        # Toggle equip/unequip
        if user_item.is_equipped:
            # Unequip the item
            user_item.is_equipped = False
            user_item.save()
        else:
            # Unequip other items of the same type for this user in the same activity
            UserItem.objects.filter(
                user=request.user,
                shop_item__item_type=user_item.shop_item.item_type,
                shop_item__activity=user_item.shop_item.activity,
            ).update(is_equipped=False)

            # Equip the selected item
            user_item.is_equipped = True
            user_item.save()

        return Response(UserItemSerializer(user_item).data)


class UserItemViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = UserItem.objects.filter(user_id=user_id).select_related('shop_item__activity')
        else:
            queryset = UserItem.objects.filter(user=self.request.user).select_related('shop_item__activity')

        activity_id = self.request.query_params.get('activity_id')
        if activity_id:
            queryset = queryset.filter(shop_item__activity_id=activity_id)

        item_type = self.request.query_params.get('item_type')
        if item_type:
            queryset = queryset.filter(shop_item__item_type=item_type)

        return queryset
