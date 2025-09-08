from django.urls import path
from .views import EnrollmentSummaryView

app_name = "enrollment_summary"

urlpatterns = [
    # final route becomes: /api/enrollments/summary
    path("summary", EnrollmentSummaryView.as_view(), name="summary"),
]
