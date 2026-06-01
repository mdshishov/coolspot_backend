from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    ClientPhoneCheckView,
    ClientRegisterView,
    LoginView,
    ChangePasswordView,
    ProfileView,
    DeactivateProfileView,
)

urlpatterns = [
    path("check-phone/", ClientPhoneCheckView.as_view(), name="check_phone"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("register/", ClientRegisterView.as_view(), name="client_register"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/deactivate/", DeactivateProfileView.as_view(), name="deactivate_profile"),
]
