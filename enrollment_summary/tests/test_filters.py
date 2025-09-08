import pytest
from django.test import RequestFactory
from enrollment_summary.filters import EnrollmentSummaryFilter
from student.models import CourseEnrollment

pytestmark = pytest.mark.django_db

def test_filter_parses_query_params(db):
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
