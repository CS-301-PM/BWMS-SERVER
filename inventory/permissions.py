from rest_framework import permissions
from authentication.models import User

class IsStoresManagerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow Stores Managers and Admins to edit products.
    Others can only view.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS: # GET, HEAD, OPTIONS
            return request.user and request.user.is_authenticated

        # Write permissions (POST, PUT, PATCH, DELETE) are only allowed to
        # Stores Managers and Admins
        return request.user and request.user.is_authenticated and (
            request.user.role in [User.Role.STORES_MANAGER, User.Role.ADMIN]
        )