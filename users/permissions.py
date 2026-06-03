from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission

User = get_user_model()

ROLE_TO_GROUP = {
    User.Role.STAFF: "staff",
}


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.STAFF


class IsClient(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.CLIENT
