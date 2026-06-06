import uuid
from decimal import Decimal, ROUND_HALF_UP

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Q
from slugify import slugify


class Category(models.Model):
    class Meta:
        ordering = ["order"]
        verbose_name = "категория"
        verbose_name_plural = "категории"

    title = models.CharField(
        "Название",
        max_length=100,
        unique=True,
    )
    slug = models.SlugField(
        unique=True,
        help_text="URL-идентификатор категории (используется в маршрутах вместо ID)",
    )
    order = models.PositiveIntegerField(
        "Порядок",
        default=0,
        help_text="Порядок отображения на сайте",
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class SubCategory(models.Model):
    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["category", "slug"],
                name="unique_subcategory_slug_per_category",
            ),
        ]
        verbose_name = "подкатегория"
        verbose_name_plural = "подкатегории"

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="subcategories",
        verbose_name="Основная категория",
    )
    title = models.CharField(
        "Название",
        max_length=100,
    )
    slug = models.SlugField(
        help_text="URL-идентификатор подкатегории (используется в маршрутах вместо ID)",
    )
    order = models.PositiveIntegerField(
        "Порядок",
        default=0,
        help_text="Порядок отображения на сайте",
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category.title} › {self.title}"


class Tag(models.Model):
    class Meta:
        ordering = ["order"]
        verbose_name = "тэг блюда"
        verbose_name_plural = "тэги блюд"

    title = models.CharField(
        "Название",
        max_length=100,
        unique=True,
    )
    slug = models.SlugField(
        unique=True,
        help_text="Значение для фильтрации через query параметр (?tag=...)",
    )
    order = models.PositiveIntegerField(
        "Порядок",
        default=0,
        help_text="Порядок отображения на сайте",
    )

    def __str__(self):
        return self.title


class Dish(models.Model):
    class Meta:
        ordering = ["title"]
        indexes = [
            models.Index(fields=["subcategory", "is_available"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(discount_percent__lte=100),
                name="discount_percent_lte_100",
            ),
            models.CheckConstraint(
                condition=Q(max_per_order__gte=1),
                name="max_per_order_gte_1",
            ),
        ]
        verbose_name = "блюдо"
        verbose_name_plural = "блюда"

    class Unit(models.TextChoices):
        G = "g", "г"
        ML = "ml", "мл"

    title = models.CharField(
        "Название",
        max_length=200,
    )
    description = models.TextField(
        "Описание",
        blank=True,
    )
    composition = models.TextField(
        "Состав",
        blank=True,
    )
    price = models.DecimalField(
        "Цена (₽)",
        max_digits=10,
        decimal_places=2,
    )
    discount_percent = models.PositiveIntegerField(
        "Скидка (%)",
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )
    amount = models.PositiveIntegerField("Вес/объём")
    unit = models.CharField(
        "Единицы измерения",
        max_length=2,
        choices=Unit.choices,
        default=Unit.G,
    )
    calories_100 = models.IntegerField(
        "Ккал (в 100 г)",
        null=True,
        blank=True,
    )
    proteins_100 = models.IntegerField(
        "Белки (в 100 г)",
        null=True,
        blank=True,
    )
    fats_100 = models.IntegerField(
        "Жиры (в 100 г)",
        null=True,
        blank=True,
    )
    carbs_100 = models.IntegerField(
        "Углеводы (в 100 г)",
        null=True,
        blank=True,
    )
    is_available = models.BooleanField(
        "Доступно",
        default=True,
        help_text="Отображается в меню и доступно для приобретения",
    )
    max_per_order = models.PositiveIntegerField(
        "Макс. в заказе",
        default=10,
        help_text="Максимальное количество в одном заказе",
        validators=[MinValueValidator(1)],
    )
    created_at = models.DateTimeField(
        "Дата создания",
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        "Дата последнего обновления",
        auto_now=True,
    )

    subcategory = models.ForeignKey(
        SubCategory,
        on_delete=models.SET_NULL,
        related_name="dishes",
        verbose_name="Подкатегория",
        null=True,
        blank=True,
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="dishes",
        verbose_name="Тэги блюда",
    )

    @property
    def main_image(self):
        return self.images.filter(image_type=DishImage.ImageType.MAIN).first()

    @property
    def card_image(self):
        return self.images.filter(image_type=DishImage.ImageType.CARD).first()

    @property
    def final_price(self):
        if not self.price:
            return Decimal("0.00")

        if not self.discount_percent:
            return self.price

        return Decimal(
            round(self.price * (100 - self.discount_percent) / 100)
        ).quantize(Decimal("0.00"))

    @property
    def total_calories(self):
        if self.calories_100 is None:
            return None
        return round(self.calories_100 * self.amount / 100)

    @property
    def total_proteins(self):
        if self.proteins_100 is None:
            return None
        return round(self.proteins_100 * self.amount / 100)

    @property
    def total_fats(self):
        if self.fats_100 is None:
            return None
        return round(self.fats_100 * self.amount / 100)

    @property
    def total_carbs(self):
        if self.carbs_100 is None:
            return None
        return round(self.carbs_100 * self.amount / 100)

    def __str__(self):
        if self.subcategory is not None:
            return f"{self.title} ({self.subcategory})"
        return self.title


def upload_image_path(instance, filename):
    ext = filename.split(".")[-1]
    return f"dishes/{uuid.uuid4()}.{ext}"


class DishImage(models.Model):
    class ImageType(models.TextChoices):
        MAIN = "main", "Главное"
        CARD = "card", "Для карточки в каталоге"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["dish", "image_type"],
                name="unique_image_type_per_dish",
            )
        ]
        verbose_name = "изображение блюда"
        verbose_name_plural = "изображения блюд"

    image = models.ImageField("Изображение", upload_to=upload_image_path)
    image_type = models.CharField(
        "Тип изображения",
        max_length=20,
        choices=ImageType.choices,
        default=ImageType.MAIN,
    )
    alt = models.CharField("Описание", max_length=255, blank=True)

    dish = models.ForeignKey(
        "Dish",
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Блюдо",
    )

    def __str__(self):
        return f"{self.dish.id}-{self.image_type}"
