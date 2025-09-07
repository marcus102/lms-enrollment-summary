from rest_framework import permissions


class IsStaffOrAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow staff or admin users.
    """
    
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.is_staff or request.user.is_superuser)
        )
