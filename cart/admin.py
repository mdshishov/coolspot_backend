from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from core.admin import BaseAdmin
from .models import Cart, CartDish


class CartDishInline(admin.TabularInline):
    model = CartDish
    extra = 0
    fields = ("dish", "quantity")
    autocomplete_fields = ("dish",)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        return False

    fields = ("user",)

    @admin.display(description="")
    def admin_actions(self, obj):
        app_label = obj._meta.app_label
        model_name = obj._meta.model_name

        view_url = reverse(f"admin:{app_label}_{model_name}_change", args=[obj.id])

        return format_html(
            """
            <a class="viewlink" style="text-decoration: none" href="{}"></a>
            """,
            view_url,
        )

    list_display = (
        "admin_actions",
        "id",
        "user",
        "total_positions",
        "total_dishes",
        "selected_price",
    )
    inlines = (CartDishInline,)
    search_fields = (
        "user__username",
        "user__full_name",
        "user__phone",
        "user__email",
    )

    def total_positions(self, obj):
        return obj.total_positions

    total_positions.short_description = "Всего позиций"

    def total_dishes(self, obj):
        return obj.total_dishes

    total_dishes.short_description = "Всего блюд"

    def selected_price(self, obj):
        return obj.selected_price

    selected_price.short_description = "Итоговая цена выбранных позиций (₽)"


@admin.register(CartDish)
class CartDishAdmin(BaseAdmin):
    list_editable = ("quantity", "is_selected")
    list_display = (
        "admin_actions",
        "cart",
        "dish",
        "is_selected",
        "quantity",
        "dish_price",
        "dish_final_price",
        "total_price",
    )
    list_select_related = ("cart", "dish")
    autocomplete_fields = ("cart", "dish")
    search_fields = (
        "cart__user__username",
        "cart__user__full_name",
        "cart__user__email",
        "cart__user__phone",
        "dish__title",
    )

    def dish_price(self, obj):
        return obj.dish.price

    dish_price.short_description = "Цена (₽)"

    def dish_final_price(self, obj):
        return obj.dish.final_price

    dish_final_price.short_description = "Цена со скидкой (₽)"

    def total_price(self, obj):
        return obj.total_price

    total_price.short_description = "Итоговая цена (₽)"
