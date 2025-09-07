"""
API views for the Enrollment Summary API
"""
import logging
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from common.djangoapps.student.models import CourseEnrollment
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx.core.lib.api.permissions import IsStaff
from opaque_keys.edx.keys import CourseKey
from opaque_keys import InvalidKeyError

from .serializers import EnrollmentSummarySerializer
from .services import EnrollmentSummaryService

logger = logging.getLogger(__name__)
User = get_user_model()


class EnrollmentSummaryPagination(PageNumberPagination):
    """Custom pagination for enrollment summary results."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class EnrollmentSummaryAPIView(APIView):
    """
    API endpoint for retrieving enrollment summaries.
    
    GET /api/enrollments/summary/?user_id=123&active=true
    
    Query Parameters:
    - user_id (int, optional): Filter by specific user ID
    - active (bool, optional): Filter by enrollment status (true/false)
    - page (int, optional): Page number for pagination
    - page_size (int, optional): Number of results per page (max 100)
    
    Returns:
    - Paginated list of enrollment summaries with course details
    """
    
    permission_classes = [IsAuthenticated, IsStaff]
    pagination_class = EnrollmentSummaryPagination
    
    @method_decorator(cache_control(max_age=300))  # 5-minute cache
    def get(self, request):
        """Handle GET requests for enrollment summaries."""
        try:
            # Validate and extract query parameters
            user_id = request.query_params.get('user_id')
            active_param = request.query_params.get('active')
            
            # Validate user_id if provided
            if user_id is not None:
                try:
                    user_id = int(user_id)
                    if not User.objects.filter(id=user_id).exists():
                        return Response(
                            {'error': f'User with ID {user_id} does not exist'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                except ValueError:
                    return Response(
                        {'error': 'user_id must be a valid integer'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Validate active parameter if provided
            active = None
            if active_param is not None:
                if active_param.lower() in ('true', '1', 'yes'):
                    active = True
                elif active_param.lower() in ('false', '0', 'no'):
                    active = False
                else:
                    return Response(
                        {'error': 'active parameter must be true or false'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Generate cache key
            cache_key = f"enrollment_summary_{user_id}_{active}_{request.user.id}"
            
            # Try to get data from cache
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.info(f"Returning cached enrollment summary data for key: {cache_key}")
                return self._paginate_response(request, cached_data)
            
            # Get enrollment summaries from service
            service = EnrollmentSummaryService()
            enrollments = service.get_enrollment_summaries(
                user_id=user_id,
                active=active
            )
            
            # Cache the results for 5 minutes
            cache.set(cache_key, enrollments, 300)
            
            return self._paginate_response(request, enrollments)
            
        except Exception as e:
            logger.exception("Error retrieving enrollment summaries")
            return Response(
                {'error': 'An error occurred while processing your request'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _paginate_response(self, request, data):
        """Paginate and serialize the response data."""
        paginator = self.pagination_class()
        paginated_data = paginator.paginate_queryset(data, request)
        
        serializer = EnrollmentSummarySerializer(paginated_data, many=True)
        response = paginator.get_paginated_response(serializer.data)
        
        # Add cache headers
        response['ETag'] = f'"enrollment-summary-{hash(str(serializer.data))}"'
        response['Cache-Control'] = 'max-age=300, public'
        
        return response