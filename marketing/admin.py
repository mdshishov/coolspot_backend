from django.contrib import admin
from django.utils.safestring import mark_safe

from core.admin import BaseAdmin
from .models import Banner, DishCollection


@admin.register(Banner)
class BannerAdmin(BaseAdmin):
    list_display = (
        "admin_actions",
        "dish",
        "order",
    )
    search_fields = (
        "dish__title",
    )
    list_editable = (
        "order",
    )
    autocomplete_fields = (
        "dish",
    )


@admin.register(DishCollection)
class DishCollectionAdmin(BaseAdmin):
    list_display = (
        "admin_actions",
        "is_active",
        "title",
        "order",
        "dishes_list",
        "dishes_count",
    )
    list_filter = (
        "is_active",
    )
    search_fields = (
        "title",
    )
    list_editable = (
        "is_active",
        "order",
    )
    filter_horizontal = (
        "dishes",
    )

    @admin.display(description="Всего блюд")
    def dishes_count(self, obj):
        return obj.dishes.count()

    @admin.display(description="Бюда")
    def dishes_list(self, obj):
        dishes = obj.dishes.all()

        links = []

        for dish in dishes:
            url = f"/admin/menu/dish/{dish.id}/change/"
            links.append(f'<a href="{url}">{dish}</a>')
        return mark_safe(", ".join(links))
