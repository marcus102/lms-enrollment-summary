"""
Serializers for the Enrollment Summary API
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class EnrollmentSummarySerializer(serializers.Serializer):
    """
    Serializer for enrollment summary data.

    Returns structured data about a user's course enrollment including
    course details and enrollment status.
    """

    user_id = serializers.IntegerField(help_text="The ID of the enrolled user")
    username = serializers.CharField(help_text="Username of the enrolled user")
    course_key = serializers.CharField(help_text="Unique identifier for the course")
    course_title = serializers.CharField(
        help_text="Display title of the course", allow_null=True
    )
    course_short_description = serializers.CharField(
        help_text="Brief description of the course", allow_null=True
    )
    enrollment_status = serializers.CharField(
        help_text="Current enrollment status (active, inactive)"
    )
    enrollment_mode = serializers.CharField(
        help_text="Mode of enrollment (audit, verified, honor, etc.)"
    )
    is_active = serializers.BooleanField(
        help_text="Whether the enrollment is currently active"
    )
    created_date = serializers.DateTimeField(
        help_text="Date when the enrollment was created"
    )
    graded_subsections_count = serializers.IntegerField(
        help_text="Number of graded subsections in the course", default=0
    )
    course_start = serializers.DateTimeField(
        help_text="Course start date", allow_null=True
    )
    course_end = serializers.DateTimeField(help_text="Course end date", allow_null=True)

    def validate(self, data):
        """Validate the enrollment summary data."""
        if not data.get("course_key"):
            raise serializers.ValidationError("Course key is required")

        if not data.get("user_id"):
            raise serializers.ValidationError("User ID is required")

        return data
