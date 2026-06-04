from rest_framework import serializers

from marketing.models import Banner, DishCollection
from menu.serializers import DishSerializer


class BannerSerializer(serializers.ModelSerializer):
    dish = DishSerializer()

    class Meta:
        model = Banner
        fields = ("dish",)

class DishCollectionSerializer(serializers.ModelSerializer):
    dishes = DishSerializer(many=True)

    class Meta:
        model = DishCollection
        fields = (
            "title",
            "dishes",
        )

class HomePageResponseSerializer(serializers.Serializer):
    banner = BannerSerializer(many=True)
    collections = DishCollectionSerializer(many=True)
