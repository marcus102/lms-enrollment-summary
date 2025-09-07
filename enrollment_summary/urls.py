"""
URL configuration for LMS Enrollment Summary API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EnrollmentSummaryViewSet

app_name = 'lms_enrollment_summary'

router = DefaultRouter()
router.register(r'summary', EnrollmentSummaryViewSet, basename='enrollment-summary')

urlpatterns = [
    path('', include(router.urls)),
]