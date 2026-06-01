from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from menu.views import MenuMetaView, MenuView

urlpatterns = [
    path("", MenuView.as_view(), name="menu"),
    path("meta/", MenuMetaView.as_view(), name="menu_meta"),
]
