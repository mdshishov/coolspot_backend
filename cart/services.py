from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework.exceptions import NotFound

from cart.models import CartDish, Cart


class CartService:
    @staticmethod
    @transaction.atomic
    def normalize_cart(cart):
        from django.db import connection

        warnings = []

        with connection.cursor() as cursor:
            cursor.execute(
                """
                    UPDATE cart_cartdish cd
                    SET quantity = d.max_per_order
                    FROM menu_dish d
                    WHERE cd.dish_id = d.id
                      AND cd.cart_id = %s
                      AND cd.quantity > d.max_per_order
                    RETURNING d.id, d.max_per_order
                """,
                [cart.id],
            )

            warnings.extend(
                {
                    "code": "max_per_order_exceeded",
                    "dish_id": dish_id,
                    "message": f"Количество уменьшено до {max_per_order}",
                }
                for dish_id, max_per_order in cursor.fetchall()
            )

            cursor.execute(
                """
                    UPDATE cart_cartdish cd
                    SET is_selected = FALSE
                    FROM menu_dish d
                    WHERE cd.dish_id = d.id
                      AND cd.cart_id = %s
                      AND d.is_available = FALSE
                      AND cd.is_selected = TRUE
                    RETURNING d.id
                """,
                [cart.id],
            )

            warnings.extend(
                {
                    "code": "dish_unavailable",
                    "dish_id": dish_id,
                    "message": "Позиция недоступна для заказа",
                }
                for (dish_id,) in cursor.fetchall()
            )

        return warnings

    @staticmethod
    def get_cart(user):
        try:
            return Cart.objects.with_dish_data().get(user=user)
        except Cart.DoesNotExist:
            raise NotFound("Корзина не найдена")

    @staticmethod
    def normalize_position(dish, quantity=None, is_selected=None):
        warnings = []

        if not dish.is_available:
            warnings.append(
                {
                    "code": "dish_unavailable",
                    "dish_id": dish.id,
                    "message": "Позиция недоступна для заказа",
                }
            )
            return {
                "warnings": warnings,
                "quantity": 1,
                "is_selected": False,
            }

        if quantity is not None:
            if quantity <= 0:
                quantity = 0
            elif dish.max_per_order is not None:
                quantity = min(quantity, dish.max_per_order)
                warnings.append(
                    {
                        "code": "max_per_order_exceeded",
                        "dish_id": dish.id,
                        "message": f"Количество уменьшено до {dish.max_per_order}",
                    }
                )

        return {
            "warnings": warnings,
            "quantity": quantity,
            "is_selected": is_selected,
        }

    @staticmethod
    @transaction.atomic
    def set_position(cart, dish, quantity=None, is_selected=None):
        position = CartDish.objects.filter(
            cart=cart,
            dish=dish,
        ).first()

        if quantity == 0:
            if position:
                position.delete()
            return None

        if position is None:
            if quantity is None:
                return None

            return CartDish.objects.create(
                cart=cart,
                dish=dish,
                quantity=quantity,
                is_selected=is_selected or True,
            )

        update_fields = []
        if quantity is not None:
            position.quantity = quantity
            update_fields.append("quantity")

        if is_selected is not None:
            position.is_selected = is_selected
            update_fields.append("is_selected")

        if update_fields:
            position.save(update_fields=update_fields)

        return position
