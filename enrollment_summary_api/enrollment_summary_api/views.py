"""
API views for the Enrollment Summary API.
"""

import logging
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from edx_rest_framework_extensions.paginators import DefaultPagination
from edx_rest_framework_extensions.permissions import IsStaff
from opaque_keys.edx.keys import CourseKey
from opaque_keys import InvalidKeyError

from .serializers import EnrollmentSummarySerializer
from .services import EnrollmentSummaryService

logger = logging.getLogger(__name__)
User = get_user_model()


class EnrollmentSummaryPagination(DefaultPagination):
    """Custom pagination for enrollment summaries."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class EnrollmentSummaryListAPIView(ListAPIView):
    """
    API view for retrieving enrollment summaries.
    
    **Supported query parameters:**
    - user_id: Filter by specific user ID
    - active: Filter by enrollment status (true/false)
    - course_key: Filter by specific course key
    - page: Page number for pagination
    - page_size: Number of items per page (max 100)
    
    **Sample Usage:**
    GET /api/enrollments/summary?user_id=123&active=true&page=1&page_size=20
    """
    
    serializer_class = EnrollmentSummarySerializer
    permission_classes = [IsAuthenticated, IsStaff | IsAdminUser]
    pagination_class = EnrollmentSummaryPagination
    
    @method_decorator(cache_control(max_age=300))  # Cache for 5 minutes
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        """
        Get filtered enrollment data based on query parameters.
        """
        # Extract and validate query parameters
        params = self._validate_query_params()
        if isinstance(params, Response):
            return []
            
        # Use service to get enrollment data
        service = EnrollmentSummaryService()
        enrollments = service.get_enrollment_summaries(**params)
        
        return enrollments
    
    def _validate_query_params(self):
        """Validate and extract query parameters."""
        params = {}
        
        # Validate user_id
        user_id = self.request.query_params.get('user_id')
        if user_id:
            try:
                user_id = int(user_id)
                if not User.objects.filter(id=user_id).exists():
                    logger.warning(f"User with ID {user_id} not found")
                    return Response(
                        {"error": f"User with ID {user_id} not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )
                params['user_id'] = user_id
            except ValueError:
                return Response(
                    {"error": "user_id must be a valid integer"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Validate active parameter
        active = self.request.query_params.get('active')
        if active is not None:
            if active.lower() in ('true', '1'):
                params['active'] = True
            elif active.lower() in ('false', '0'):
                params['active'] = False
            else:
                return Response(
                    {"error": "active must be 'true' or 'false'"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Validate course_key
        course_key = self.request.query_params.get('course_key')
        if course_key:
            try:
                CourseKey.from_string(course_key)
                params['course_key'] = course_key
            except InvalidKeyError:
                return Response(
                    {"error": "Invalid course key format"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return params
    
    def list(self, request, *args, **kwargs):
        """Override list to handle validation errors."""
        params = self._validate_query_params()
        if isinstance(params, Response):
            return params
            
        return super().list(request, *args, **kwargs)