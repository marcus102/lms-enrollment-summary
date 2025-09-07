"""
Service layer for enrollment summary business logic
"""

import logging
from typing import List, Dict, Any, Optional
from django.contrib.auth import get_user_model
from django.db import connection

from common.djangoapps.student.models import CourseEnrollment
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from xmodule.modulestore.django import modulestore

logger = logging.getLogger(__name__)
User = get_user_model()


class EnrollmentSummaryService:
    """
    Service class for handling enrollment summary operations.

    This service aggregates data from multiple sources:
    - CourseEnrollment (MySQL): enrollment data
    - CourseOverview (MySQL): cached course metadata
    - Modulestore (MongoDB): course structure for graded subsections
    """

    def get_enrollment_summaries(
        self, user_id: Optional[int] = None, active: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve enrollment summaries with optional filtering.

        Args:
            user_id: Filter by specific user ID
            active: Filter by enrollment active status

        Returns:
            List of enrollment summary dictionaries
        """
        logger.info(
            f"Fetching enrollment summaries - user_id: {user_id}, active: {active}"
        )

        # Build the base queryset
        enrollments = CourseEnrollment.objects.select_related("user").all()

        # Apply filters
        if user_id is not None:
            enrollments = enrollments.filter(user_id=user_id)

        if active is not None:
            enrollments = enrollments.filter(is_active=active)

        # Order by most recent enrollments first
        enrollments = enrollments.order_by("-created")

        # Convert to list and enrich with course data
        enrollment_summaries = []

        for enrollment in enrollments:
            try:
                summary = self._build_enrollment_summary(enrollment)
                if summary:  # Only add if we successfully built the summary
                    enrollment_summaries.append(summary)
            except Exception as e:
                logger.warning(
                    f"Failed to build summary for enrollment {enrollment.id}: {e}"
                )
                continue

        logger.info(f"Retrieved {len(enrollment_summaries)} enrollment summaries")
        return enrollment_summaries

    def _build_enrollment_summary(
        self, enrollment: CourseEnrollment
    ) -> Optional[Dict[str, Any]]:
        """
        Build a complete enrollment summary from an enrollment object.

        Args:
            enrollment: CourseEnrollment instance

        Returns:
            Dictionary containing enrollment summary data or None if failed
        """
        try:
            # Get course overview for cached metadata
            try:
                course_overview = CourseOverview.objects.get(id=enrollment.course_id)
            except CourseOverview.DoesNotExist:
                logger.warning(f"CourseOverview not found for {enrollment.course_id}")
                course_overview = None

            # Count graded subsections from modulestore
            graded_count = self._count_graded_subsections(enrollment.course_id)

            # Build the summary dictionary
            summary = {
                "user_id": enrollment.user.id,
                "username": enrollment.user.username,
                "course_key": str(enrollment.course_id),
                "course_title": (
                    course_overview.display_name
                    if course_overview
                    else str(enrollment.course_id)
                ),
                "course_short_description": (
                    course_overview.short_description if course_overview else None
                ),
                "enrollment_status": "active" if enrollment.is_active else "inactive",
                "enrollment_mode": enrollment.mode,
                "is_active": enrollment.is_active,
                "created_date": enrollment.created,
                "graded_subsections_count": graded_count,
                "course_start": course_overview.start if course_overview else None,
                "course_end": course_overview.end if course_overview else None,
            }

            return summary

        except Exception as e:
            logger.error(f"Error building enrollment summary for {enrollment.id}: {e}")
            return None

    def _count_graded_subsections(self, course_key) -> int:
        """
        Count graded subsections in a course using the modulestore.

        Args:
            course_key: Course key to count subsections for

        Returns:
            Number of graded subsections, 0 if unable to determine
        """
        try:
            store = modulestore()
            course = store.get_course(course_key, depth=2)

            if not course:
                logger.warning(f"Course not found in modulestore: {course_key}")
                return 0

            graded_count = 0
            for chapter in course.children:
                chapter_descriptor = store.get_item(chapter)
                for subsection_key in chapter_descriptor.children:
                    subsection = store.get_item(subsection_key)
                    if getattr(subsection, "graded", False):
                        graded_count += 1

            return graded_count

        except Exception as e:
            logger.warning(f"Error counting graded subsections for {course_key}: {e}")
            return 0
