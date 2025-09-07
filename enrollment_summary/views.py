from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from django.contrib.auth.models import User
from .serializers import EnrollmentSummarySerializer
from .services import EnrollmentSummaryService
import logging

logger = logging.getLogger(__name__)


class EnrollmentSummaryPagination(PageNumberPagination):
    """
    Custom pagination for enrollment summaries.
    """
    page_size_query_param = 'page_size'
    max_page_size = getattr(settings, 'ENROLLMENT_SUMMARY_MAX_PAGE_SIZE', 100)
    page_size = getattr(settings, 'ENROLLMENT_SUMMARY_PAGE_SIZE', 20)


class EnrollmentSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for enrollment summary API.
    Provides read-only access to enrollment data.
    """
    serializer_class = EnrollmentSummarySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = EnrollmentSummaryPagination
    
    @method_decorator(cache_control(max_age=300))  # 5 minutes cache
    def list(self, request):
        """
        GET /api/enrollments/summary/
        
        Query Parameters:
        - user_id: Filter by specific user ID
        - active: Filter by active status (true/false)
        - page: Page number
        - page_size: Items per page
        """
        try:
            # Validate and extract query parameters
            user_id = self._get_user_id_param(request)
            active = self._get_active_param(request)
            
            # Get pagination parameters
            page = int(request.query_params.get('page', 1))
            page_size = min(
                int(request.query_params.get('page_size', self.pagination_class.page_size)),
                self.pagination_class.max_page_size
            )
            
            # Get enrollment summaries
            summaries, total_count = EnrollmentSummaryService.get_enrollment_summaries(
                user_id=user_id,
                active=active,
                page_size=page_size,
                page=page
            )
            
            # Serialize data
            serializer = self.serializer_class(summaries, many=True)
            
            # Calculate pagination info
            total_pages = (total_count + page_size - 1) // page_size
            
            response_data = {
                'count': total_count,
                'page': page,
                'page_size': page_size,
                'total_pages': total_pages,
                'next': self._get_next_url(request, page, total_pages),
                'previous': self._get_previous_url(request, page),
                'results': serializer.data
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response(
                {'error': f'Invalid parameter: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error in enrollment summary API: {e}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_user_id_param(self, request):
        """Validate and extract user_id parameter."""
        user_id_str = request.query_params.get('user_id')
        if user_id_str is not None:
            try:
                user_id = int(user_id_str)
                # Verify user exists
                if not User.objects.filter(id=user_id).exists():
                    raise ValueError(f'User with ID {user_id} does not exist')
                return user_id
            except (ValueError, TypeError):
                raise ValueError('user_id must be a valid integer')
        return None
    
    def _get_active_param(self, request):
        """Validate and extract active parameter."""
        active_str = request.query_params.get('active')
        if active_str is not None:
            if active_str.lower() in ['true', '1', 'yes']:
                return True
            elif active_str.lower() in ['false', '0', 'no']:
                return False
            else:
                raise ValueError('active must be true or false')
        return None
    
    def _get_next_url(self, request, current_page, total_pages):
        """Generate next page URL."""
        if current_page < total_pages:
            params = request.query_params.copy()
            params['page'] = current_page + 1
            return f"{request.build_absolute_uri('?')}{params.urlencode()}"
        return None
    
    def _get_previous_url(self, request, current_page):
        """Generate previous page URL."""
        if current_page > 1:
            params = request.query_params.copy()
            params['page'] = current_page - 1
            return f"{request.build_absolute_uri('?')}{params.urlencode()}"
        return None