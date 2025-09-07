"""
Service functions for enrollment summary operations
"""
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from student.models import CourseEnrollment
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from opaque_keys.edx.keys import CourseKey
from opaque_keys import InvalidKeyError
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class EnrollmentSummaryService:
    """
    Service class for enrollment summary operations
    """
    
    @staticmethod
    def get_enrollment_summary(user_id=None, active=None, course_key=None):
        """
        Get enrollment summary data with optional filters
        
        Args:
            user_id (int, optional): Filter by user ID
            active (bool, optional): Filter by active status
            course_key (str, optional): Filter by course key
            
        Returns:
            QuerySet: Filtered enrollment data
        """
        queryset = CourseEnrollment.objects.select_related('user').all()
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
            
        if active is not None:
            queryset = queryset.filter(is_active=active)
            
        if course_key:
            try:
                course_key_obj = CourseKey.from_string(course_key)
                queryset = queryset.filter(course_id=course_key_obj)
            except InvalidKeyError:
                logger.warning(f"Invalid course key provided: {course_key}")
                return queryset.none()
        
        return queryset.order_by('-created')
    
    @staticmethod
    def get_user_enrollment_stats(user_id):
        """
        Get enrollment statistics for a specific user
        
        Args:
            user_id (int): User ID
            
        Returns:
            dict: User enrollment statistics
        """
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
            
        enrollments = CourseEnrollment.objects.filter(user_id=user_id)
        
        return {
            'user_id': user_id,
            'username': user.username,
            'total_enrollments': enrollments.count(),
            'active_enrollments': enrollments.filter(is_active=True).count(),
            'inactive_enrollments': enrollments.filter(is_active=False).count(),
        }
