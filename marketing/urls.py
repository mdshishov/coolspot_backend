from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from marketing.views import HomeView


urlpatterns = [
    path("home/", HomeView.as_view(), name="marketing_home"),
]
