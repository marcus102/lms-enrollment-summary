import types
from enrollment_summary.serializers import EnrollmentSummarySerializer

def test_enrollment_summary_serializer_basic():
    # Dummy enrollment-like object
    obj = types.SimpleNamespace(
        course_id="course-v1:EDX+TST101+2025",
        is_active=True,
        user_id=42,
    )

    context = {
        "course_titles": {"course-v1:EDX+TST101+2025": "Test Course"},
        "graded_counts": {"course-v1:EDX+TST101+2025": 7},
    }

    ser = EnrollmentSummarySerializer(instance=obj, context=context)
    data = ser.data

    assert data["course_key"] == "course-v1:EDX+TST101+2025"
    assert data["course_title"] == "Test Course"
    assert data["enrollment_status"] == "active"
    assert data["graded_subsections_count"] == 7
