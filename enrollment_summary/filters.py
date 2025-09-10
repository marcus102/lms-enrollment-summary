import django_filters


def get_course_enrollment_model():
    """Dynamically import CourseEnrollment from available paths."""
    import_paths = [
        "common.djangoapps.student.models",
        "lms.djangoapps.student.models",
        "student.models",
        "openedx.core.djangoapps.student.models",
    ]

    for path in import_paths:
        try:
            module = __import__(path, fromlist=["CourseEnrollment"])
            return getattr(module, "CourseEnrollment")
        except (ImportError, AttributeError):
            continue

    raise ImportError("CourseEnrollment model not found in any known location")


# Initialize the model
CourseEnrollment = get_course_enrollment_model()


class EnrollmentSummaryFilter(django_filters.FilterSet):
    user_id = django_filters.NumberFilter(field_name="user_id")
    active = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = CourseEnrollment
        fields = ["user_id", "active"]
