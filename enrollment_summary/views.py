"""
Views for LMS Enrollment Summary API
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from django.http import Http404

from student.models import CourseEnrollment
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from opaque_keys.edx.keys import CourseKey
from opaque_keys import InvalidKeyError

from .serializers import EnrollmentSummarySerializer
from .permissions import IsStaffOrSuperuser

User = get_user_model()


class EnrollmentSummaryPagination(PageNumberPagination):
    """
    Custom pagination for enrollment summary
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class EnrollmentSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for enrollment summary data
    
    Provides read-only access to enrollment summaries with filtering capabilities.
    Only accessible to staff users and superusers.
    """
    serializer_class = EnrollmentSummarySerializer
    permission_classes = [IsAuthenticated, IsStaffOrSuperuser]
    pagination_class = EnrollmentSummaryPagination
    
    def get_queryset(self):
        """
        Get filtered queryset based on query parameters
        """
        queryset = CourseEnrollment.objects.select_related('user').all()
        
        # Filter by user_id if provided
        user_id = self.request.query_params.get('user_id')
        if user_id:
            try:
                user_id = int(user_id)
                queryset = queryset.filter(user_id=user_id)
            except (ValueError, TypeError):
                # Invalid user_id format
                queryset = queryset.none()
        
        # Filter by active status if provided
        active = self.request.query_params.get('active')
        if active is not None:
            if active.lower() in ['true', '1', 'yes']:
                queryset = queryset.filter(is_active=True)
            elif active.lower() in ['false', '0', 'no']:
                queryset = queryset.filter(is_active=False)
        
        # Filter by course_key if provided (bonus feature)
        course_key = self.request.query_params.get('course_key')
        if course_key:
            try:
                course_key = CourseKey.from_string(course_key)
                queryset = queryset.filter(course_id=course_key)
            except InvalidKeyError:
                # Invalid course key format
                queryset = queryset.none()
        
        return queryset.order_by('-created')
    
    @method_decorator(cache_control(max_age=300))  # 5 minutes cache
    def list(self, request, *args, **kwargs):
        """
        List enrollment summaries with caching headers
        """
        response = super().list(request, *args, **kwargs)
        
        # Add custom headers
        response['X-API-Version'] = '1.0'
        response['X-Total-Count'] = self.get_queryset().count()
        
        return response
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve is not supported for this endpoint
        """
        return Response(
            {'detail': 'Retrieve operation is not supported. Use list with filters instead.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )