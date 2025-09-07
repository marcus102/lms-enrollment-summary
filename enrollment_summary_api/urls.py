"""
URL configuration for the Enrollment Summary API.
"""

from django.urls import path
from .views import EnrollmentSummaryListAPIView

app_name = "enrollment_summary_api"

urlpatterns = [
    path(
        "summary",
        EnrollmentSummaryListAPIView.as_view(),
        name="enrollment-summary-list"
    ),
]