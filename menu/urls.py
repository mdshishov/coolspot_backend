from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from menu.views import MenuMetaView, MenuView, DishDetailView

urlpatterns = [
    path("", MenuView.as_view(), name="menu"),
    path("meta/", MenuMetaView.as_view(), name="menu_meta"),
    path("dishes/<int:pk>", DishDetailView.as_view(), name="dish_detail"),
]
