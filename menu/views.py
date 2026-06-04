from django.db.models import Q
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
)
from rest_framework.generics import ListAPIView, get_object_or_404, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from menu.models import Category, Tag, Dish
from menu.serializers import (
    CategorySerializer,
    TagSerializer,
    MenuMetaSerializer,
    DishSerializer,
)


@extend_schema(
    summary="Информация о категориях и тэгах меню",
    responses=MenuMetaSerializer,
)
class MenuMetaView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        categories = Category.objects.prefetch_related("subcategories")

        tags = Tag.objects.all()

        return Response(
            {
                "categories": CategorySerializer(categories, many=True).data,
                "tags": TagSerializer(tags, many=True).data,
            }
        )


@extend_schema(
    summary="Список блюд со всеми данными",
    parameters=[
        OpenApiParameter(
            name="category",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Slug категории",
        ),
        OpenApiParameter(
            name="subcategory",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Slug подкатегории",
        ),
        OpenApiParameter(
            name="tag",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Slug тэга",
        ),
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Поиск по названию, описанию и составу блюда",
        ),
    ],
)
class MenuView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = DishSerializer

    def get_queryset(self):
        qs = (
            Dish.objects.filter(is_available=True)
            .select_related(
                "subcategory",
                "subcategory__category",
            )
            .prefetch_related(
                "tags",
                "images",
            )
            .distinct()
        )

        category_slug = self.request.query_params.get("category")
        subcategory_slug = self.request.query_params.get("subcategory")
        tag_slug = self.request.query_params.get("tag")
        search = self.request.query_params.get("search")

        if category_slug:
            qs = qs.filter(subcategory__category__slug=category_slug)

        if subcategory_slug:
            qs = qs.filter(subcategory__slug=subcategory_slug)

        if tag_slug:
            qs = qs.filter(tags__slug=tag_slug)

        if search:
            qs = qs.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(composition__icontains=search)
            )

        return qs


@extend_schema(
    summary="Информация о позиции меню",
    responses=DishSerializer,
)
class DishDetailView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = DishSerializer

    def get_queryset(self):
        return Dish.objects.select_related(
            "subcategory",
            "subcategory__category",
        ).prefetch_related(
            "tags",
            "images",
        )
