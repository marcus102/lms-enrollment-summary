"""
Serializers for LMS Enrollment Summary API
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from student.models import CourseEnrollment
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

User = get_user_model()


class EnrollmentSummarySerializer(serializers.Serializer):
    """
    Serializer for enrollment summary data
    """
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    course_key = serializers.CharField()
    course_title = serializers.CharField()
    enrollment_status = serializers.CharField()
    is_active = serializers.BooleanField()
    enrollment_date = serializers.DateTimeField()
    graded_subsections_count = serializers.IntegerField()

    def to_representation(self, instance):
        """
        Convert enrollment instance to dictionary representation
        """
        try:
            course_overview = CourseOverview.objects.get(id=instance.course_id)
            graded_subsections_count = self._get_graded_subsections_count(course_overview)
        except CourseOverview.DoesNotExist:
            course_overview = None
            graded_subsections_count = 0

        return {
            'user_id': instance.user.id,
            'username': instance.user.username,
            'course_key': str(instance.course_id),
            'course_title': course_overview.display_name if course_overview else 'Unknown Course',
            'enrollment_status': instance.mode,
            'is_active': instance.is_active,
            'enrollment_date': instance.created,
            'graded_subsections_count': graded_subsections_count,
        }

    def _get_graded_subsections_count(self, course_overview):
        """
        Get count of graded subsections for a course
        This is a simplified implementation - in production you might want to
        cache this or compute it more efficiently
        """
        try:
            from xmodule.modulestore.django import modulestore
            course = modulestore().get_course(course_overview.id, depth=2)
            if course:
                graded_count = 0
                for chapter in course.get_children():
                    for section in chapter.get_children():
                        if getattr(section, 'graded', False):
                            graded_count += 1
                return graded_count
        except Exception:
            # Fallback to a simple count based on course overview
            pass
        return 0