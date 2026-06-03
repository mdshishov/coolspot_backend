from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CartView,
    CartSummaryView,
    SetPositionView,
)

urlpatterns = [
    path("", CartView.as_view(), name="cart"),
    path("summary/", CartSummaryView.as_view(), name="cart_summary"),
    path("set-position/", SetPositionView.as_view(), name="cart_set_position"),
]
