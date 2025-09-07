"""
URL configuration for the Enrollment Summary API
"""
from django.urls import path
from .views import EnrollmentSummaryAPIView

app_name = 'enrollment_summary_api'

urlpatterns = [
    path('summary/', EnrollmentSummaryAPIView.as_view(), name='enrollment-summary'),
]