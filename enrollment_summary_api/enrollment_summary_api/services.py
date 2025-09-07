"""
Business logic services for the Enrollment Summary API.
"""

import logging
from typing import List, Dict, Any, Optional
from django.contrib.auth import get_user_model
from django.core.cache import cache
from opaque_keys.edx.keys import CourseKey
from common.djangoapps.student.models import CourseEnrollment
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from xmodule.modulestore.django import modulestore

logger = logging.getLogger(__name__)
User = get_user_model()


class EnrollmentSummaryService:
    """
    Service class for handling enrollment summary business logic.
    """
    
    CACHE_TIMEOUT = 300  # 5 minutes
    
    def get_enrollment_summaries(
        self, 
        user_id: Optional[int] = None,
        active: Optional[bool] = None,
        course_key: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get enrollment summaries with optional filtering.
        
        Args:
            user_id: Filter by specific user ID
            active: Filter by enrollment active status
            course_key: Filter by specific course key
            
        Returns:
            List of enrollment summary dictionaries
        """
        
        # Build cache key
        cache_key = self._build_cache_key(user_id, active, course_key)
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            logger.info(f"Cache hit for enrollment summaries: {cache_key}")
            return cached_result
        
        # Build queryset with filters
        enrollments_qs = CourseEnrollment.objects.select_related('user')
        
        if user_id:
            enrollments_qs = enrollments_qs.filter(user_id=user_id)
        
        if active is not None:
            enrollments_qs = enrollments_qs.filter(is_active=active)
        
        if course_key:
            enrollments_qs = enrollments_qs.filter(course_id=course_key)
        
        # Order by most recent enrollments first
        enrollments_qs = enrollments_qs.order_by('-created')
        
        # Process enrollments and gather course data
        summaries = []
        course_keys_to_fetch = set()
        
        # Collect all course keys first
        for enrollment in enrollments_qs:
            course_keys_to_fetch.add(str(enrollment.course_id))
        
        # Bulk fetch course overviews
        course_overviews = self._get_course_overviews(list(course_keys_to_fetch))
        
        # Build summaries
        for enrollment in enrollments_qs:
            course_key_str = str(enrollment.course_id)
            course_overview = course_overviews.get(course_key_str, {})
            
            summary = {
                'user_id': enrollment.user.id,
                'username': enrollment.user.username,
                'course_key': course_key_str,
                'course_title': course_overview.get('display_name', 'Unknown Course'),
                'enrollment_status': self._get_enrollment_status(enrollment),
                'is_active': enrollment.is_active,
                'enrollment_date': enrollment.created,
                'graded_subsections_count': self._get_graded_subsections_count(
                    enrollment.course_id
                ),
                'course_start': course_overview.get('start'),
                'course_end': course_overview.get('end'),
            }
            summaries.append(summary)
        
        # Cache the results
        cache.set(cache_key, summaries, self.CACHE_TIMEOUT)
        logger.info(f"Cached enrollment summaries: {cache_key}")
        
        return summaries
    
    def _build_cache_key(
        self, 
        user_id: Optional[int], 
        active: Optional[bool], 
        course_key: Optional[str]
    ) -> str:
        """Build a cache key for the given parameters."""
        key_parts = ['enrollment_summaries']
        if user_id:
            key_parts.append(f'user_{user_id}')
        if active is not None:
            key_parts.append(f'active_{active}')
        if course_key:
            key_parts.append(f'course_{course_key.replace(":", "_").replace("+", "_")}')
        
        return ':'.join(key_parts)
    
    def _get_course_overviews(self, course_keys: List[str]) -> Dict[str, Dict]:
        """
        Bulk fetch course overviews for the given course keys.
        
        Returns:
            Dictionary mapping course key strings to course overview data
        """
        overviews = {}
        
        try:
            # Convert string keys to CourseKey objects
            course_key_objects = []
            for key_str in course_keys:
                try:
                    course_key_objects.append(CourseKey.from_string(key_str))
                except Exception as e:
                    logger.warning(f"Invalid course key: {key_str}, error: {e}")
                    continue
            
            # Fetch course overviews
            course_overviews = CourseOverview.objects.filter(
                id__in=course_key_objects
            )
            
            for overview in course_overviews:
                overviews[str(overview.id)] = {
                    'display_name': overview.display_name or 'Untitled Course',
                    'start': overview.start,
                    'end': overview.end,
                }
                
        except Exception as e:
            logger.error(f"Error fetching course overviews: {e}")
        
        return overviews
    
    def _get_enrollment_status(self, enrollment: CourseEnrollment) -> str:
        """Get human-readable enrollment status."""
        if enrollment.is_active:
            return "active"
        else:
            return "inactive"
    
    def _get_graded_subsections_count(self, course_key: CourseKey) -> int:
        """
        Get the count of graded subsections for a course.
        
        This is a simplified implementation. In a production environment,
        you might want to cache this data or compute it more efficiently.
        """
        cache_key = f"graded_subsections_count:{course_key}"
        cached_count = cache.get(cache_key)
        if cached_count is not None:
            return cached_count
        
        try:
            store = modulestore()
            course = store.get_course(course_key)
            if not course:
                return 0
            
            graded_count = 0
            for chapter in course.get_children():
                for section in chapter.get_children():
                    if getattr(section, 'graded', False):
                        graded_count += 1
            
            # Cache for 1 hour
            cache.set(cache_key, graded_count, 3600)
            return graded_count
            
        except Exception as e:
            logger.warning(
                f"Error counting graded subsections for {course_key}: {e}"
            )
            return 0