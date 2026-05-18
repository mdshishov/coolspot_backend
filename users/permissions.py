from rest_framework.permissions import BasePermission

from .models import CustomUser

ROLE_TO_GROUP = {
    CustomUser.Role.STAFF: 'staff',
}


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return (
                request.user.is_authenticated and
                request.user.is_manager
        )


class IsClient(BasePermission):
    def has_permission(self, request, view):
        return (
                request.user.is_authenticated and
                request.user.is_client
        )
