from django.contrib import admin
from django.db import models
from django.db.models import F, Sum, DecimalField, ExpressionWrapper
from django.forms import Textarea
from django.utils.html import format_html

from core.admin import BaseAdmin
from .models import Order, OrderDish


class OrderDishInline(admin.TabularInline):
    class Media:
        js = ("admin/js/orderdish_inline.js",)

    model = OrderDish
    extra = 0
    readonly_fields = ("total_price",)
    fields = ("dish", "dish_title", "quantity", "dish_price", "total_price")
    autocomplete_fields = ("dish",)

    def total_price(self, obj):
        return obj.total_price

    total_price.short_description = "Итоговая цена"


@admin.register(Order)
class OrderAdmin(BaseAdmin):
    formfield_overrides = {models.TextField: {"widget": Textarea(attrs={"rows": 3})}}

    list_display = (
        "admin_actions",
        "id",
        "status_badge",
        "user",
        "address",
        "total_positions",
        "total_dishes",
        "total_price",
        "created_at",
    )

    def total_positions(self, obj):
        return obj.total_positions

    total_positions.short_description = "Всего позиций"

    def total_dishes(self, obj):
        return obj.total_dishes

    total_dishes.short_description = "Всего блюд"

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "id",
        "address",
        "user__full_name",
        "user__phone",
        "username",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "total_price",
    )

    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "status",
                    "address",
                    "comment",
                    "user",
                    "total_price",
                )
            },
        ),
        (
            "Даты",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)

        if not obj:
            fieldsets = tuple(fs for fs in fieldsets if fs[0] != "Даты")

        return fieldsets

    inlines = [OrderDishInline]

    @admin.display(description="Роль")
    def status_badge(self, obj):
        colors = {
            "new": "#3b82f6",
            "cooking": "#f59e0b",
            "delivery": "#8b5cf6",
            "done": "#10b981",
            "cancelled": "#ef4444",
        }

        return format_html(
            """
            <span style="
                background:{};
                color:white;
                padding:4px 10px;
                border-radius:4px;
            ">
                {}
            </span>
            """,
            colors.get(obj.status, "#3b82f6"),
            obj.get_status_display(),
        )


@admin.register(OrderDish)
class OrderDishAdmin(BaseAdmin):
    class Media:
        js = ("admin/js/orderdish_totalprice.js",)

    list_display = (
        "admin_actions",
        "order",
        "dish_title",
        "quantity",
        "dish_price",
        "total_price",
    )

    @admin.display(description="Итоговая цена (₽)")
    def total_price(self, obj):
        return format_html(
            '<span id="total_price_preview">{}</span>', obj.total_price or 0
        )

    search_fields = (
        "dish_title",
        "order__id",
        "dish__title",
    )

    def get_fields(self, request, obj=None):
        if obj:
            return [
                "order",
                "dish",
                "dish_title",
                "quantity",
                "dish_price",
                "total_price",
            ]
        return [
            "order",
            "dish",
            "quantity",
        ]

    def get_readonly_fields(self, request, obj=None):
        readonly = ["total_price"]

        if obj:
            readonly += [
                "order",
                "dish",
            ]

        return readonly
