from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EnrollmentSummaryViewSet

router = DefaultRouter()
router.register(r'summary', EnrollmentSummaryViewSet, basename='enrollment-summary')

urlpatterns = [
    path('', include(router.urls)),
]