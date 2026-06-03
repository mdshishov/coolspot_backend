from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from menu.models import Dish
from menu.serializers import DishSerializer
from .models import CartDish, Cart


class CartDishSerializer(serializers.ModelSerializer):
    dish = DishSerializer(read_only=True)

    quantity_changed = serializers.SerializerMethodField()
    is_available = serializers.BooleanField(
        source="dish.is_available",
        read_only=True,
    )

    class Meta:
        model = CartDish
        fields = (
            "id",
            "dish",
            "quantity",
            "is_available",
            "is_selected",
            "quantity_changed",
        )

    @extend_schema_field(bool)
    def get_quantity_changed(self, obj):
        changed_ids = self.context.get("changed_ids", set())
        return obj.id in changed_ids


class CartSerializer(serializers.ModelSerializer):
    positions = CartDishSerializer(many=True)
    total_dishes = serializers.IntegerField(read_only=True)
    selected_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = (
            "id",
            "total_dishes",
            "selected_price",
            "positions",
        )

    @extend_schema_field(int)
    def get_selected_price(self, obj):
        return int(obj.selected_price)


class CartDishSummarySerializer(serializers.ModelSerializer):
    dish_id = serializers.PrimaryKeyRelatedField(source="dish", read_only=True)

    class Meta:
        model = CartDish
        fields = ("dish_id", "quantity")


class CartSummarySerializer(serializers.ModelSerializer):
    positions = CartDishSummarySerializer(many=True)
    total_dishes = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ("total_dishes", "positions")


class CartSetPositionSerializer(serializers.Serializer):
    dish_id = serializers.PrimaryKeyRelatedField(
        queryset=Dish.objects.all(),
        source="dish",
        error_messages={
            "does_not_exist": "Позиция не найдена",
        },
    )
    quantity = serializers.IntegerField(
        min_value=0,
        required=False,
    )
    is_selected = serializers.BooleanField(
        required=False,
    )


class CartWarningSerializer(serializers.Serializer):
    code = serializers.CharField()
    dish_id = serializers.IntegerField()
    message = serializers.CharField()


class SetPositionResponseSerializer(serializers.Serializer):
    cart = CartSummarySerializer()
    warnings = CartWarningSerializer(many=True, required=False)
