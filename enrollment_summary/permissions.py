"""
Custom permissions for the Enrollment Summary API
"""
from rest_framework.permissions import BasePermission


class IsStaffOrInstructor(BasePermission):
    """
    Custom permission to only allow staff or instructors to access enrollment data.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has staff or instructor permissions.
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Global staff always have access
        if request.user.is_staff:
            return True
        
        # Check if user is an instructor for any course
        # This is a simplified check - in production, you might want to
        # check course-specific instructor permissions
        return hasattr(request.user, 'courseaccessrole_set') and \
               request.user.courseaccessrole_set.filter(role__in=['instructor', 'staff']).exists()