"""
Serializers for the Enrollment Summary API.
"""

from rest_framework import serializers


class EnrollmentSummarySerializer(serializers.Serializer):
    """
    Serializer for enrollment summary data.
    """
    
    user_id = serializers.IntegerField(
        help_text="The ID of the enrolled user"
    )
    username = serializers.CharField(
        max_length=150,
        help_text="The username of the enrolled user"
    )
    course_key = serializers.CharField(
        max_length=255,
        help_text="The course key (opaque key string)"
    )
    course_title = serializers.CharField(
        max_length=255,
        allow_blank=True,
        help_text="The display name of the course"
    )
    enrollment_status = serializers.CharField(
        max_length=50,
        help_text="Current enrollment status (active, inactive, etc.)"
    )
    is_active = serializers.BooleanField(
        help_text="Whether the enrollment is currently active"
    )
    enrollment_date = serializers.DateTimeField(
        help_text="When the user enrolled in the course"
    )
    graded_subsections_count = serializers.IntegerField(
        default=0,
        help_text="Number of graded subsections in the course"
    )
    course_start = serializers.DateTimeField(
        allow_null=True,
        help_text="Course start date"
    )
    course_end = serializers.DateTimeField(
        allow_null=True,
        help_text="Course end date"
    )