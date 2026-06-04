from django.db import transaction
from rest_framework import serializers

from cart.services import CartService
from orders.models import Order, OrderDish

class OrderService:
    @staticmethod
    @transaction.atomic
    def create_order(*, user, address, comment=""):
        cart = CartService.get_cart(user)

        positions = list(
            cart.positions
            .select_related("dish")
            .filter(is_selected=True)
        )

        if not positions:
            raise serializers.ValidationError(
                "Не выбрано ни одной позиции"
            )

        warnings = CartService.normalize_cart(cart)

        if warnings:
            return {
                "order": None,
                "warnings": warnings,
            }

        order = Order.objects.create(
            user=user,
            address=address,
            comment=comment,
        )

        for position in positions:
            OrderDish.objects.create(
                order=order,
                dish=position.dish,
                quantity=position.quantity,
            )

        cart.positions.filter(
            is_selected=True,
        ).delete()

        return {
            "order": order,
            "warnings": [],
        }

    @staticmethod
    def ensure_editable(order):
        if order.status != Order.Status.NEW:
            raise serializers.ValidationError("Заказ нельзя изменить")
