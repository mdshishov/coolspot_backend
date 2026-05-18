import uuid

from django.db import models
from slugify import slugify


class Category(models.Model):
    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    title = models.CharField('Название', max_length=100, unique=True)
    slug = models.SlugField(unique=True, help_text='URL-идентификатор категории (используется в маршрутах вместо ID)')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class SubCategory(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['category', 'slug'],
                name='unique_subcategory_slug_per_category',
            )
        ]
        verbose_name = 'подкатегория'
        verbose_name_plural = 'подкатегории'

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='subcategories',
        verbose_name='Основная категория',
    )

    title = models.CharField('Название', max_length=100)
    slug = models.SlugField(help_text='URL-идентификатор подкатегории (используется в маршрутах вместо ID)')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.category.title} › {self.title}'


class Tag(models.Model):
    class Meta:
        verbose_name = 'тэг блюда'
        verbose_name_plural = 'тэги блюд'

    title = models.CharField('Название', max_length=100, unique=True)
    slug = models.SlugField(unique=True, help_text='Значение для фильтрации через query параметр (?tag=...)')

    def __str__(self):
        return self.title


class Dish(models.Model):
    class Meta:
        ordering = ['title']
        indexes = [
            models.Index(fields=['is_available']),
            models.Index(fields=['subcategory', 'is_available']),
        ]
        verbose_name = 'блюдо'
        verbose_name_plural = 'блюда'

    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    composition = models.TextField('Состав')
    price = models.DecimalField('Цена (₽)', max_digits=10, decimal_places=2)
    discount_percent = models.PositiveIntegerField('Скидка (%)', default=0)
    weight = models.PositiveIntegerField('Вес (г)')
    is_available = models.BooleanField('Доступно', default=True,
                                       help_text='Отображается в меню и доступно для приобретения')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата последнего обновления', auto_now=True)
    max_quantity_per_order = models.PositiveIntegerField(
        'Макс. в заказе',
        default=10,
        help_text='Максимальное количество в одном заказе'
    )

    subcategory = models.ForeignKey(
        SubCategory,
        on_delete=models.PROTECT,
        related_name='dishes',
        verbose_name='Подкатегория'
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='dishes',
        verbose_name='Тэги блюда',
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
            return 0
        if not self.discount_percent:
            return self.price

        return round(
            self.price *
            (100 - self.discount_percent) / 100
        )

    def __str__(self):
        return self.title


def upload_image_path(instance, filename):
    ext = filename.split('.')[-1]
    return f'dishes/{uuid.uuid4()}.{ext}'


class DishImage(models.Model):
    class ImageType(models.TextChoices):
        MAIN = 'main', 'Главное'
        CARD = 'card', 'Для карточки в каталоге'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['dish', 'image_type'],
                name='unique_image_type_per_dish',
            )
        ]
        verbose_name = 'изображение блюда'
        verbose_name_plural = 'изображения блюд'

    image = models.ImageField('Изображение', upload_to=upload_image_path)
    image_type = models.CharField(
        'Тип изображения',
        max_length=20,
        choices=ImageType.choices,
        default=ImageType.MAIN,
    )
    alt = models.CharField('Описание', max_length=255, blank=True)

    dish = models.ForeignKey(
        'Dish',
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Блюдо',
    )

    def __str__(self):
        return f'{self.dish.id}-{self.image_type}'
