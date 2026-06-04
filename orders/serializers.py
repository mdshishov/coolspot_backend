from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from menu.serializers import DishSerializer
from .models import OrderDish, Order


class OrderDishSerializer(serializers.ModelSerializer):
    dish = DishSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()
    dish_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderDish
        fields = (
            "dish",
            "dish_title",
            "dish_price",
            "quantity",
            "total_price",
        )

    @extend_schema_field(int)
    def get_total_price(self, obj):
        return int(obj.total_price)

    @extend_schema_field(int)
    def get_dish_price(self, obj):
        return int(obj.dish_price)


class OrderSerializer(serializers.ModelSerializer):
    positions = OrderDishSerializer(many=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            "id",
            "status",
            "address",
            "comment",
            "created_at",
            "total_price",
            "positions",
        )

    @extend_schema_field(int)
    def get_total_price(self, obj):
        return int(obj.total_price)


class CreateOrderSerializer(serializers.Serializer):
    address = serializers.CharField()
    comment = serializers.CharField(required=False, allow_blank=True)


class UpdateOrderSerializer(serializers.Serializer):
    address = serializers.CharField(required=False)
    comment = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    def validate(self, attrs):
        if "address" not in attrs and "comment" not in attrs:
            raise serializers.ValidationError(
                "Передайте хотя бы одно поле: address или comment"
            )

        return attrs
