import django_filters
from student.models import CourseEnrollment

class EnrollmentSummaryFilter(django_filters.FilterSet):
    user_id = django_filters.NumberFilter(field_name="user_id")
    active = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = CourseEnrollment
        fields = ["user_id", "active"]
