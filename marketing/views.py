from django.db.models import Prefetch, Count, Q
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from marketing.models import Banner, DishCollection
from marketing.serializers import HomePageResponseSerializer
from menu.models import Dish

@extend_schema(
    summary="Инфрмация о баннере и подборках на главной странице",
    responses=HomePageResponseSerializer,
)
class HomeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        banner = (
            Banner.objects.filter(dish__is_available=True)
            .select_related(
                "dish",
                "dish__subcategory",
                "dish__subcategory__category",
            )
            .prefetch_related(
                "dish__tags",
                "dish__images",
            )
        )

        collections = (
            DishCollection.objects.filter(is_active=True)
            .annotate(
                available_dishes_count=Count(
                    "dishes",
                    filter=Q(dishes__is_available=True),
                    distinct=True,
                )
            )
            .filter(available_dishes_count__gt=0)
            .prefetch_related(
                Prefetch(
                    "dishes",
                    queryset=Dish.objects.filter(is_available=True)
                    .select_related(
                        "subcategory",
                        "subcategory__category",
                    )
                    .prefetch_related(
                        "tags",
                        "images",
                    ),
                )
            )
        )

        serializer = HomePageResponseSerializer(
            {
                "banner": banner,
                "collections": collections,
            }
        )

        return Response(serializer.data)
