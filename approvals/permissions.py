from rest_framework import permissions
from authentication.models import User
from .models import Approval

class IsAssignedApprover(permissions.BasePermission):
    """
    Custom permission to only allow the assigned approver for a specific stage
    to make a decision on it.
    """

    def has_object_permission(self, request, view, obj):
        # The user must be the assigned approver for this approval stage
        return obj.approver == request.user

class IsCorrectRoleForStage(permissions.BasePermission):
    """
    Custom permission to ensure a user only interacts with approvals
    for the stage that matches their role.
    """

    def has_permission(self, request, view):
        user = request.user
        # Map user roles to the approval stages they can handle
        role_stage_map = {
            User.Role.STORES_MANAGER: Approval.Stage.STORES,
            User.Role.PROCUREMENT_OFFICER: Approval.Stage.PROCUREMENT,
            User.Role.CFO: Approval.Stage.CFO,
        }
        # If the user's role isn't in the map, they have no permission for any stage
        if user.role not in role_stage_map:
            return False

        # For safe methods (GET), allow them to see approvals for their stage
        if request.method in permissions.SAFE_METHODS:
            return True

        # For write methods (POST, PATCH), we need to check the object's stage
        # This will be handled in the view using get_queryset
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        role_stage_map = {
            User.Role.STORES_MANAGER: Approval.Stage.STORES,
            User.Role.PROCUREMENT_OFFICER: Approval.Stage.PROCUREMENT,
            User.Role.CFO: Approval.Stage.CFO,
        }
        # Check if the approval object's stage matches the user's role
        return obj.stage == role_stage_map.get(user.role)