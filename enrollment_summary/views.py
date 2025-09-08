from django.db.models import Count
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from student.models import CourseEnrollment
from course_overviews.models import CourseOverview

from .serializers import EnrollmentSummarySerializer
from .filters import EnrollmentSummaryFilter
from .pagination import StandardResultsSetPagination
from .permissions import IsSelfOrStaff

# Try to import PersistentSubsectionGrade across supported paths
try:
    from lms.djangoapps.grades.models import PersistentSubsectionGrade
except Exception:  # pragma: no cover (fallback)
    try:
        from grades.models import PersistentSubsectionGrade  # older paths
    except Exception:
        PersistentSubsectionGrade = None


class EnrollmentSummaryView(ListAPIView):
    """
    GET /api/enrollments/summary?user_id=&active=
    Returns: course_key, course_title, enrollment_status, graded_subsections_count
    """
    permission_classes = [IsAuthenticated, IsSelfOrStaff]
    serializer_class = EnrollmentSummarySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = EnrollmentSummaryFilter
    pagination_class = StandardResultsSetPagination

    @method_decorator(cache_page(60 * 5))  # 5-minute server-side cache
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        """
        Start from enrollments for the requested user (or current user).
        We don't use select_related('course') because CourseEnrollment stores course_id (no FK).
        """
        params = self.request.query_params
        user_id = params.get("user_id")
        if user_id is None:
            user_id = self.request.user.id
        else:
            # permissions.IsSelfOrStaff already validated it's int or staff
            user_id = int(user_id)

        qs = CourseEnrollment.objects.filter(user_id=user_id)
        # active filter will be applied by the FilterSet; we keep base qs constrained by user.
        return qs

    def list(self, request, *args, **kwargs):
        # Apply filters and paginate
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        objects = page if page is not None else queryset

        # Collect course_ids visible on this page to keep lookups fast
        course_ids = [str(e.course_id) for e in objects]

        # Titles
        titles = {
            str(rec["id"]): rec["display_name"]
            for rec in CourseOverview.objects.filter(id__in=course_ids).values("id", "display_name")
        }

        # Graded subsections count per course for this user
        graded_counts = {}
        if PersistentSubsectionGrade and course_ids:
            user_id = request.query_params.get("user_id") or request.user.id
            agg = (
                PersistentSubsectionGrade.objects
                .filter(user_id=user_id, course_id__in=course_ids)
                .filter(possible_graded__gt=0)           # graded-only subsections
                .values("course_id")
                .annotate(count=Count("id"))
            )
            graded_counts = {str(row["course_id"]): int(row["count"]) for row in agg}

        # Serialize
        serializer = self.get_serializer(
            objects, many=True,
            context={"course_titles": titles, "graded_counts": graded_counts},
        )

        if page is not None:
            response = self.get_paginated_response(serializer.data)
        else:
            response = Response(serializer.data)

        # Caching headers for clients/proxies (pairs with cache_page)
        response["Cache-Control"] = "public, max-age=300"
        return response
