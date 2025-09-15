from rest_framework import permissions
from authentication.models import User

class IsDepartmentDeanOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow Department Deans to create requests.
    Stores Managers can view all and update status.
    """

    def has_permission(self, request, view):
        # Anyone can view if authenticated (SAFE_METHODS = GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # Only Department Deans can create requests
        return request.user.is_authenticated and request.user.role == User.Role.DEPARTMENT_DEAN

    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Deans can only edit their own requests if pending
        if user.role == User.Role.DEPARTMENT_DEAN:
            return obj.requested_by == user and obj.status == obj.Status.PENDING

        # Stores Managers can update requests (for approval)
        if user.role == User.Role.STORES_MANAGER:
            return True

        # Admins can do anything
        if user.role == User.Role.ADMIN:
            return True

        return False


class CanViewAllRequests(permissions.BasePermission):
    """
    Permission to allow Stores Managers, Procurement, CFO, and Admin to view all requests.
    Department Deans can only view their own requests.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        # Everyone can view if authenticated, but object-level filtering will apply
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Stores Managers, Procurement, CFO, and Admin can view all requests
        if user.role in [User.Role.STORES_MANAGER, User.Role.PROCUREMENT_OFFICER, 
                        User.Role.CFO, User.Role.ADMIN]:
            return True
            
        # Department Deans can only view their own requests
        if user.role == User.Role.DEPARTMENT_DEAN:
            return obj.requested_by == user
            
        return False