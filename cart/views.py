from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.serializers import (
    CartSerializer,
    CartSummarySerializer,
    CartSetPositionSerializer,
    SetPositionResponseSerializer,
)
from cart.services import CartService

User = get_user_model()


@extend_schema(
    summary="Получение полной информации о корзине с предварительной нормализацией",
    responses=CartSerializer,
)
class CartView(APIView):
    @transaction.atomic
    def get(self, request):
        cart = CartService.get_cart(request.user)
        changed_ids = CartService.normalize_cart(cart)
        cart = CartService.get_cart(request.user)
        serializer = CartSerializer(
            cart,
            context={"changed_ids": changed_ids},
        )

        return Response(serializer.data)


@extend_schema(
    summary="Получение краткой информации о корзине",
    responses=CartSummarySerializer,
)
class CartSummaryView(APIView):
    def get(self, request):
        cart = CartService.get_cart(request.user)

        serializer = CartSummarySerializer(cart)
        return Response(serializer.data)


@extend_schema(
    summary="Добавление/редактирование/удаление позиции (возвращает краткую информацию о корзине)",
    request=CartSetPositionSerializer,
    responses=SetPositionResponseSerializer,
)
class SetPositionView(APIView):
    @transaction.atomic
    def post(self, request):
        serializer = CartSetPositionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = CartService.get_cart(request.user)

        dish = serializer.validated_data["dish"]
        quantity = serializer.validated_data.get("quantity")
        is_selected = serializer.validated_data.get("is_selected")

        warnings = []
        if not dish.is_available:
            warnings.append(
                {
                    "code": "dish_unavailable",
                    "dish_id": dish.id,
                    "message": "Позиция недоступна для заказа",
                }
            )

        normalized = CartService.normalize_position(
            dish=dish,
            quantity=quantity,
            is_selected=is_selected,
        )
        CartService.set_position(
            cart=cart,
            dish=dish,
            quantity=normalized.get("quantity"),
            is_selected=normalized.get("is_selected"),
        )

        cart = CartService.get_cart(request.user)
        return Response(
            {
                "cart": CartSummarySerializer(cart).data,
                "warnings": warnings,
            }
        )
