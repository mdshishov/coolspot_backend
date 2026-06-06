from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from menu.models import Tag, SubCategory, Category, Dish, DishImage


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("title", "slug")


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ("title", "slug")


class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True)

    class Meta:
        model = Category
        fields = (
            "title",
            "slug",
            "subcategories",
        )


class CategoryShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("title", "slug")


class SubCategoryWithCategorySerializer(serializers.ModelSerializer):
    category = CategoryShortSerializer(read_only=True)

    class Meta:
        model = SubCategory
        fields = (
            "slug",
            "title",
            "category",
        )


class MenuMetaSerializer(serializers.Serializer):
    categories = CategorySerializer(many=True)
    tags = TagSerializer(many=True)


class PriceSerializer(serializers.Serializer):
    base = serializers.IntegerField()
    discount_percent = serializers.IntegerField()
    final = serializers.IntegerField()


class WeightSerializer(serializers.Serializer):
    value = serializers.IntegerField()
    unit = serializers.CharField()
    display = serializers.CharField()


class NutritionValuesSerializer(serializers.Serializer):
    calories = serializers.IntegerField(allow_null=True)
    proteins = serializers.IntegerField(allow_null=True)
    fats = serializers.IntegerField(allow_null=True)
    carbs = serializers.IntegerField(allow_null=True)


class NutritionSerializer(serializers.Serializer):
    per_100 = NutritionValuesSerializer()
    total = NutritionValuesSerializer()


class DishImageSerializer(serializers.Serializer):
    url = serializers.URLField()
    alt = serializers.CharField()


class DishImagesSerializer(serializers.Serializer):
    main = DishImageSerializer(allow_null=True)
    card = DishImageSerializer(allow_null=True)


class DishSerializer(serializers.ModelSerializer):
    subcategory = SubCategoryWithCategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    images = serializers.SerializerMethodField()
    weight = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    nutrition = serializers.SerializerMethodField()

    class Meta:
        model = Dish
        fields = (
            "id",
            "is_available",
            "title",
            "description",
            "composition",
            "price",
            "weight",
            "nutrition",
            "max_per_order",
            "subcategory",
            "tags",
            "images",
        )

    @extend_schema_field(WeightSerializer)
    def get_weight(self, obj):
        return {
            "value": obj.amount,
            "unit": obj.get_unit_display(),
            "display": f"{obj.amount} {obj.get_unit_display()}",
        }

    @extend_schema_field(PriceSerializer)
    def get_price(self, obj):
        return {
            "base": int(obj.price),
            "discount_percent": obj.discount_percent,
            "final": int(obj.final_price),
        }

    @extend_schema_field(DishImagesSerializer)
    def get_images(self, obj):
        images_map = {image.image_type: image for image in obj.images.all()}

        result = {}
        for image_type, _ in DishImage.ImageType.choices:
            image = images_map.get(image_type)

            if image:
                result[image_type] = {
                    "url": image.image.url,
                    "alt": image.alt,
                }
            else:
                result[image_type] = None

        return result

    @extend_schema_field(NutritionSerializer)
    def get_nutrition(self, obj):
        return {
            "per_100": {
                "calories": obj.calories_100,
                "proteins": obj.proteins_100,
                "fats": obj.fats_100,
                "carbs": obj.carbs_100,
            },
            "total": {
                "calories": obj.total_calories,
                "proteins": obj.total_proteins,
                "fats": obj.total_fats,
                "carbs": obj.total_carbs,
            },
        }
