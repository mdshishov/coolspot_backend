from django.db import models

from menu.models import Dish


class Banner(models.Model):
    class Meta:
        verbose_name = "позиция баннера"
        verbose_name_plural = "позиции баннера"
        ordering = ["order"]

    order = models.PositiveIntegerField("Порядок", default=0)

    dish = models.OneToOneField(
        Dish,
        on_delete=models.CASCADE,
        verbose_name="Блюдо",
    )


class DishCollection(models.Model):
    class Meta:
        verbose_name = "подборка блюд"
        verbose_name_plural = "подборки блюд"
        ordering = ["order", "title"]

    title = models.CharField("Название", max_length=200)
    is_active = models.BooleanField("Активно", default=True)
    order = models.PositiveIntegerField("Порядок", default=0)

    dishes = models.ManyToManyField(
        Dish,
        blank=True,
        related_name="dishes",
        verbose_name="Блюда",
    )
