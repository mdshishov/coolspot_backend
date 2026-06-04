from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from menu.views import MenuMetaView, MenuView, DishDetailView
from orders.views import (
    CreateOrderView,
    OrderDetailView,
    CancelOrderView,
    OrdersView,
    UpdateOrderView,
)

urlpatterns = [
    path("", OrdersView.as_view(), name="orders"),
    path("create/", CreateOrderView.as_view(), name="create_order"),
    path("<int:pk>/", OrderDetailView.as_view(), name="order_detail"),
    path("<int:pk>/update", UpdateOrderView.as_view(), name="updte_order"),
    path("<int:pk>/cancel", CancelOrderView.as_view(), name="cancel_order"),
]
