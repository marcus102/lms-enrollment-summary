"""
Custom permissions for LMS Enrollment Summary API
"""
from rest_framework.permissions import BasePermission


class IsStaffOrSuperuser(BasePermission):
    """
    Custom permission to only allow staff users or superusers to access the API
    """
    
    def has_permission(self, request, view):
        """
        Check if user has staff or superuser permissions
        """
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.is_staff or request.user.is_superuser)
        )