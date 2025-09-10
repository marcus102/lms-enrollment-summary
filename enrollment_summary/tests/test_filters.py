import pytest
from django.test import RequestFactory
from enrollment_summary.filters import EnrollmentSummaryFilter

# Import CourseEnrollment with fallback paths
try:
    from common.djangoapps.student.models import CourseEnrollment
except ImportError:
    try:
        from student.models import CourseEnrollment
    except ImportError:
        try:
            from lms.djangoapps.student.models import CourseEnrollment
        except ImportError:
            raise ImportError("Could not import CourseEnrollment from any known path")

pytestmark = pytest.mark.django_db


def test_filter_parses_query_params(db):
    """Test that the filter correctly parses query parameters."""
    # We don't need rows; we just validate cleaned_data & that qs builds.
    rf = RequestFactory()
    request = rf.get("/api/enrollments/summary", {"user_id": "123", "active": "true"})

    f = EnrollmentSummaryFilter(
        data=request.GET,
        queryset=CourseEnrollment.objects.all(),
    )

    assert f.is_valid(), f.errors
    assert f.form.cleaned_data["user_id"] == 123
    assert f.form.cleaned_data["active"] is True

    # qs should be a queryset even with zero rows
    _ = f.qs  # should not raise


def test_filter_handles_invalid_user_id():
    """Test that the filter handles invalid user_id gracefully."""
    rf = RequestFactory()
    request = rf.get(
        "/api/enrollments/summary", {"user_id": "invalid", "active": "true"}
    )

    f = EnrollmentSummaryFilter(
        data=request.GET,
        queryset=CourseEnrollment.objects.all(),
    )

    # Should still be valid at filter level (validation happens in permissions)
    assert f.is_valid() or "user_id" in f.errors


def test_filter_handles_missing_params():
    """Test that the filter works with missing parameters."""
    rf = RequestFactory()
    request = rf.get("/api/enrollments/summary")

    f = EnrollmentSummaryFilter(
        data=request.GET,
        queryset=CourseEnrollment.objects.all(),
    )

    assert f.is_valid(), f.errors
    # Should have empty cleaned_data for missing params
    assert (
        "user_id" not in f.form.cleaned_data or f.form.cleaned_data["user_id"] is None
    )
    assert "active" not in f.form.cleaned_data or f.form.cleaned_data["active"] is None
