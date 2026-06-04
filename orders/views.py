from django.db import transaction
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import status, serializers
from rest_framework.generics import get_object_or_404, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order
from orders.serializers import (
    CreateOrderSerializer,
    OrderSerializer,
    UpdateOrderSerializer,
)
from orders.services import OrderService


@extend_schema(
    summary="Информация о всех заказах пользователя",
    responses=OrderSerializer(many=True),
)
class OrdersView(ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            "positions"
        )


@extend_schema(
    summary="Информация о заказе",
    responses=OrderSerializer,
)
class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            "positions"
        )


@extend_schema(
    summary="Создание заказа из выбранных в корзине позиций",
    responses=OrderSerializer,
)
class CreateOrderView(APIView):
    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = OrderService.create_order(
            user=request.user,
            address=serializer.validated_data["address"],
            comment=serializer.validated_data.get("comment", ""),
        )

        if result["warnings"]:
            return Response(
                {"warnings": result["warnings"]},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            OrderSerializer(result["order"]).data,
            status=status.HTTP_201_CREATED,
        )

@extend_schema(
    summary="Изменение заказа (адрес и комментарий)",
    request=UpdateOrderSerializer,
    responses=OrderSerializer,
)
class UpdateOrderView(APIView):
    @transaction.atomic
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        OrderService.ensure_editable(order)

        serializer = UpdateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        update_fields = []
        if "address" in serializer.validated_data:
            order.address = serializer.validated_data["address"]
            update_fields.append("address")
        if "comment" in serializer.validated_data:
            order.comment = serializer.validated_data["comment"]
            update_fields.append("comment")

        order.save(update_fields=update_fields)

        return Response(OrderSerializer(order).data)


@extend_schema(
    summary="Отмена заказа",
    responses=OrderSerializer,
)
class CancelOrderView(APIView):
    @transaction.atomic
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        OrderService.ensure_editable(order)

        order.status = Order.Status.CANCELLED
        order.save(update_fields=["status"])

        return Response(OrderSerializer(order).data)
