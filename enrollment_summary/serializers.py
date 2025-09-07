from rest_framework import serializers
from django.contrib.auth.models import User
from student.models import CourseEnrollment
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview


class EnrollmentSummarySerializer(serializers.Serializer):
    """
    Serializer for enrollment summary data.
    """
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    course_key = serializers.CharField()
    course_title = serializers.CharField()
    enrollment_status = serializers.CharField()
    is_active = serializers.BooleanField()
    created = serializers.DateTimeField()
    graded_subsections_count = serializers.IntegerField()
    
    class Meta:
        fields = [
            'user_id', 'username', 'course_key', 'course_title',
            'enrollment_status', 'is_active', 'created', 'graded_subsections_count'
        ]
