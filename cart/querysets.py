from django.db import models
from django.db.models import Prefetch


class CartQuerySet(models.QuerySet):
    def with_dish_data(self):
        from .models import CartDish

        return self.prefetch_related(
            Prefetch(
                "positions",
                queryset=CartDish.objects.select_related(
                    "dish",
                    "dish__subcategory",
                    "dish__subcategory__category",
                ).prefetch_related(
                    "dish__tags",
                    "dish__images",
                ),
            )
        )
