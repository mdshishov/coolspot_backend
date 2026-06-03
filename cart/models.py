from decimal import Decimal

from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum, Q, ExpressionWrapper, F, DecimalField

from cart.querysets import CartQuerySet
from users.models import CustomUser
from menu.models import Dish


class Cart(models.Model):
    class Meta:
        verbose_name = "корзина"
        verbose_name_plural = "корзины"

    objects = CartQuerySet.as_manager()

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="Пользователь",
    )

    def save(self, *args, **kwargs):
        if self.pk and Cart.objects.filter(pk=self.pk).exists():
            raise ValidationError("Корзину нельзя изменять после создания")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.user_id is not None:
            raise ValidationError(
                "Нельзя удалить корзину, пока существует пользователь"
            )
        super().delete(*args, **kwargs)

    @property
    def total_positions(self):
        return self.positions.count()

    @property
    def total_dishes(self):
        return self.positions.aggregate(total=Sum("quantity"))["total"] or 0

    @property
    def selected_price(self):
        positions = self.positions.select_related("dish").filter(is_selected=True)
        return sum(item.total_price for item in positions) or Decimal("0.00")

    def __str__(self):
        return f"Корзина {self.user.username}"


class CartDish(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "dish"], name="unique_dish_in_cart"
            ),
            models.CheckConstraint(
                condition=Q(quantity__gte=1),
                name="quantity_gte_1",
            ),
        ]
        verbose_name = "позиция в корзине"
        verbose_name_plural = "позиции в корзинах"

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="positions",
        verbose_name="Корзина",
    )
    dish = models.ForeignKey(
        Dish,
        on_delete=models.CASCADE,
        related_name="cart_positions",
        verbose_name="Блюдо",
    )

    quantity = models.PositiveIntegerField(
        "Кол-во",
        default=1,
        validators=[MinValueValidator(1)],
    )
    is_selected = models.BooleanField(
        "Выбрано для заказа",
        default=True,
    )

    @property
    def total_price(self):
        return self.dish.final_price * self.quantity

    def __str__(self):
        if self.dish:
            return f"{self.dish.title} x {self.quantity}"
        return f"Неизвестная позиция x {self.quantity}"

    def clean(self):
        super().clean()
        if self.dish and self.dish.max_per_order is not None:
            if self.quantity > self.dish.max_per_order:
                raise ValidationError(
                    {
                        "quantity": f"Максимум для блюда: {self.dish.max_per_order}",
                    }
                )
