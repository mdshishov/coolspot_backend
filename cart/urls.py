from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("", name="cart"),
    path("summary/", name="cart_summary"),
]
