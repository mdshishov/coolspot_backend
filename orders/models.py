from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from decimal import Decimal

from menu.models import Dish
from users.models import CustomUser


class Order(models.Model):
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    class Status(models.TextChoices):
        NEW = 'new', 'Новый'
        COOKING = 'cooking', 'Готовится'
        DELIVERY = 'delivery', 'Доставляется'
        DONE = 'done', 'Завершён'
        CANCELLED = 'cancelled', 'Отменён'

    status = models.CharField(
        'Статус',
        max_length=10,
        choices=Status.choices,
        default=Status.NEW,
    )
    address = models.TextField('Адрес доставки')
    comment = models.TextField('Комментарий', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата последнего обновления', auto_now=True)

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name='Пользователь',
        help_text='Заказ может быть оформлен только клиентом',
    )
    dishes = models.ManyToManyField(
        Dish,
        through='OrderDish',
        related_name='orders',
        verbose_name='Блюда',
    )
    total_price = models.DecimalField(
        'Итоговая цена (₽)',
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Пересчитывается автоматически при сохранении',
    )

    @property
    def total_positions(self):
        return self.positions.count()

    @property
    def total_dishes(self):
        return self.positions.aggregate(total=Sum('quantity'))['total'] or 0

    def __str__(self):
        return f'Заказ #{self.id}'

    def refresh_total_price(self):
        self.total_price = sum(
            position.total_price
            for position in self.positions.all()
        )
        self.save(update_fields=['total_price'])

    def clean(self):
        super().clean()
        if self.user:
            if not self.user.is_client_role:
                raise ValidationError({'user': 'Только клиенты могут оформлять заказ'})
        if self._state.adding:
            if not self.user:
                raise ValidationError({'user': 'Укажите клиента'})


class OrderDish(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['order', 'dish'],
                name='unique_dish_in_order'
            )
        ]
        verbose_name = 'позиция в заказе'
        verbose_name_plural = 'позиции в заказах'

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='positions',
        verbose_name='Заказ'
    )
    dish = models.ForeignKey(
        Dish,
        on_delete=models.SET_NULL,
        related_name='order_positions',
        null=True,
        blank=True,
        verbose_name='Блюдо'
    )

    quantity = models.PositiveIntegerField(
        'Кол-во',
        default=1,
        validators=[MinValueValidator(1)],
    )
    dish_price = models.DecimalField(
        'Цена блюда (₽)',
        max_digits=10,
        decimal_places=2,
        blank=True,
        help_text='Сохраняется автоматически из блюда при создании позиции и не меняется при изменеии исходного блюда',
    )
    dish_title = models.CharField(
        'Название блюда',
        max_length=200,
        blank=True,
        help_text='Сохраняется автоматически из блюда при создании позиции и не меняется при изменении исходного блюда',
    )

    @property
    def total_price(self):
        if self.dish_price and  self.quantity:
            return self.dish_price * self.quantity
        return 0;

    def __str__(self):
        if self.dish_title:
            return f'{self.dish_title} x {self.quantity}'
        return f'Неизвестная позиция x {self.quantity}'

    def clean(self):
        super().clean()
        if self._state.adding:
            if self.dish and self.dish.max_quantity_per_order is not None:
                if self.quantity > self.dish.max_quantity_per_order:
                    raise ValidationError({
                        'quantity': f'Максимум для блюда: {self.dish.max_quantity_per_order}'
                    })
            if not self.dish:
                raise ValidationError({
                    'dish': 'Укажите блюдо'
                })

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.dish_title = self.dish.title
            self.dish_price = self.dish.price

        super().save(*args, **kwargs)

        self.order.refresh_total_price()
