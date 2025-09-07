from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.core.cache import cache
from student.models import CourseEnrollment
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from xmodule.modulestore.django import modulestore
from opaque_keys.edx.keys import CourseKey
import logging

logger = logging.getLogger(__name__)


class EnrollmentSummaryService:
    """
    Service class for handling enrollment summary business logic.
    """
    
    @staticmethod
    def get_enrollment_summaries(user_id=None, active=None, page_size=20, page=1):
        """
        Get enrollment summaries with optional filtering.
        
        Args:
            user_id (int, optional): Filter by specific user ID
            active (bool, optional): Filter by active status
            page_size (int): Number of items per page
            page (int): Page number
            
        Returns:
            tuple: (queryset, total_count)
        """
        try:
            # Build the base query
            enrollments = CourseEnrollment.objects.select_related(
                'user', 'course'
            ).all()
            
            # Apply filters
            if user_id is not None:
                enrollments = enrollments.filter(user_id=user_id)
                
            if active is not None:
                enrollments = enrollments.filter(is_active=active)
            
            # Get total count before pagination
            total_count = enrollments.count()
            
            # Apply pagination
            start = (page - 1) * page_size
            end = start + page_size
            enrollments = enrollments[start:end]
            
            # Convert to summary data
            summaries = []
            for enrollment in enrollments:
                try:
                    course_overview = CourseOverview.objects.get(
                        id=enrollment.course_id
                    )
                    course_title = course_overview.display_name
                except CourseOverview.DoesNotExist:
                    course_title = str(enrollment.course_id)
                
                # Get graded subsections count
                graded_count = EnrollmentSummaryService._get_graded_subsections_count(
                    enrollment.course_id
                )
                
                summary = {
                    'user_id': enrollment.user.id,
                    'username': enrollment.user.username,
                    'course_key': str(enrollment.course_id),
                    'course_title': course_title,
                    'enrollment_status': enrollment.mode,
                    'is_active': enrollment.is_active,
                    'created': enrollment.created,
                    'graded_subsections_count': graded_count,
                }
                summaries.append(summary)
                
            return summaries, total_count
            
        except Exception as e:
            logger.error(f"Error getting enrollment summaries: {e}")
            raise
    
    @staticmethod
    def _get_graded_subsections_count(course_key):
        """
        Get the count of graded subsections for a course.
        Uses caching to improve performance.
        """
        cache_key = f"graded_subsections_count_{course_key}"
        count = cache.get(cache_key)
        
        if count is None:
            try:
                store = modulestore()
                course = store.get_course(course_key)
                
                if course:
                    count = 0
                    for chapter in course.get_children():
                        for sequential in chapter.get_children():
                            if getattr(sequential, 'graded', False):
                                count += 1
                else:
                    count = 0
                    
                # Cache for 1 hour
                cache.set(cache_key, count, 3600)
                
            except Exception as e:
                logger.warning(f"Error counting graded subsections for {course_key}: {e}")
                count = 0
                
        return count