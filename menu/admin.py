from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db import models
from django.forms import Textarea

from core.admin import BaseAdmin
from .models import (
    Category,
    SubCategory,
    Tag,
    Dish,
    DishImage,
)


class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 0
    prepopulated_fields = {"slug": ("title",)}


class DishImageInline(admin.TabularInline):
    class Media:
        js = ("admin/js/image_inline_preview.js",)

    model = DishImage
    extra = 0
    fields = (
        "image",
        "image_preview",
        "image_type",
        "alt",
    )
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                """<div class="inline_image_preview">
                    <img src="{}" height="100" style="border-radius: 4px;" />
                </div>""",
                obj.image.url,
            )
        return format_html('<div class="inline_image_preview">{}</div>', "")

    image_preview.short_description = "Превью"


@admin.register(Category)
class CategoryAdmin(BaseAdmin):
    list_display = (
        "admin_actions",
        "id",
        "title",
        "slug",
        "subcategories_count",
        "subcategories_list",
    )
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    inlines = (SubCategoryInline,)

    def subcategories_count(self, obj):
        return obj.subcategories.count()

    subcategories_count.short_description = "Кол-во подкатегорий"

    @admin.display(description="Подкатегории")
    def subcategories_list(self, obj):
        subs = obj.subcategories.all()

        links = []

        for sub in subs:
            url = f"/admin/menu/subcategory/{sub.id}/change/"
            links.append(f'<a href="{url}">{sub}</a>')
        return mark_safe(", ".join(links))


@admin.register(SubCategory)
class SubCategoryAdmin(BaseAdmin):
    list_display = (
        "admin_actions",
        "id",
        "title",
        "slug",
        "category",
    )
    list_filter = ("category",)
    search_fields = (
        "title",
        "slug",
        "category__title",
    )
    autocomplete_fields = ("category",)
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Tag)
class TagAdmin(BaseAdmin):
    list_display = ("admin_actions", "id", "title", "slug", "dishes_list")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}

    @admin.display(description="Блюда")
    def dishes_list(self, obj):
        dishes = obj.dishes.all()

        links = []

        for dish in dishes:
            url = f"/admin/menu/dish/{dish.id}/change/"
            links.append(f'<a href="{url}">{dish}</a>')
        return mark_safe(", ".join(links))


@admin.register(DishImage)
class DishImageAdmin(BaseAdmin):
    class Media:
        js = ("admin/js/dish_image_preview.js",)

    list_display = (
        "admin_actions",
        "id",
        "dish",
        "image_type",
        "image_preview",
    )
    list_filter = ("image_type",)
    autocomplete_fields = ("dish",)
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                """<div id="dish_image_preview">
                    <img src="{}" height="50" style="border-radius: 4px;" />
                </div>""",
                obj.image.url,
            )
        return format_html('<div id="dish_image_preview">{}</div>', "")

    image_preview.short_description = "Превью"


@admin.register(Dish)
class DishAdmin(BaseAdmin):
    formfield_overrides = {models.TextField: {"widget": Textarea(attrs={"rows": 3})}}

    class Media:
        js = ("admin/js/dish_discount.js",)

    list_display = (
        "admin_actions",
        "is_available",
        "id",
        "images_preview",
        "title",
        "subcategory",
        "tags_list",
        "price",
        "final_price",
        "discount_percent",
        "amount",
        "unit",
        "calories_100",
        "proteins_100",
        "fats_100",
        "carbs_100",
        "created_at",
        "updated_at",
    )

    @admin.display(description="Цена со скидкой (₽)")
    def final_price(self, obj):
        return format_html(
            '<span id="final_price_preview">{}</span>', obj.final_price or 0
        )

    @admin.display(description="Тэги")
    def tags_list(self, obj):
        tags = obj.tags.all()

        links = []

        for tag in tags:
            url = f"/admin/users/customuser/{tag.id}/change/"
            links.append(f'<a href="{url}">{tag}</a>')
        return mark_safe(", ".join(links))

    list_filter = (
        "is_available",
        "subcategory__category",
        "subcategory",
        "tags",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
        "composition",
        "subcategory__title",
        "subcategory__category__title",
    )

    autocomplete_fields = (
        "subcategory",
        "tags",
    )

    list_editable = (
        "is_available",
        "price",
        "discount_percent",
        "amount",
        "unit",
        "calories_100",
        "proteins_100",
        "fats_100",
        "carbs_100",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "final_price",
    )

    filter_horizontal = ("tags",)

    inlines = (DishImageInline,)

    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "title",
                    "description",
                    "composition",
                    "subcategory",
                    "is_available",
                    "max_per_order",
                    "tags",
                )
            },
        ),
        (
            "Цена",
            {
                "fields": (
                    "price",
                    "discount_percent",
                    "final_price",
                )
            },
        ),
        (
            "Вес и КБЖУ",
            {
                "fields": (
                    "amount",
                    "unit",
                    "calories_100",
                    "proteins_100",
                    "fats_100",
                    "carbs_100",
                )
            },
        ),
        (
            "Служебные поля",
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
            fieldsets = tuple(fs for fs in fieldsets if fs[0] != "Служебные поля")

        return fieldsets

    def images_preview(self, obj):
        images = []

        for img in (obj.main_image, obj.card_image):
            if img and img.image:
                images.append(
                    f'<img src="{img.image.url}" height="40" style="border-radius: 4px;" />'
                )

        if not images:
            return "—"

        return format_html(
            '<div style="display: flex; gap: 4px;">{}</div>', mark_safe("".join(images))
        )

    images_preview.short_description = "Изображения"
