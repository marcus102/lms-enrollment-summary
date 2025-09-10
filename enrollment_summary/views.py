from django.db.models import Count
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import EnrollmentSummarySerializer
from .filters import EnrollmentSummaryFilter
from .pagination import StandardResultsSetPagination
from .permissions import IsSelfOrStaff


# Dynamic imports with comprehensive fallbacks
def get_course_enrollment_model():
    """Dynamically import CourseEnrollment from available paths."""
    import_paths = [
        "common.djangoapps.student.models",
        "lms.djangoapps.student.models",
        "student.models",
        "openedx.core.djangoapps.student.models",
    ]

    for path in import_paths:
        try:
            module = __import__(path, fromlist=["CourseEnrollment"])
            return getattr(module, "CourseEnrollment")
        except (ImportError, AttributeError):
            continue

    raise ImportError("CourseEnrollment model not found in any known location")


def get_course_overview_model():
    """Dynamically import CourseOverview from available paths."""
    import_paths = [
        "openedx.core.djangoapps.content.course_overviews.models",
        "lms.djangoapps.course_overviews.models",
        "course_overviews.models",
        "common.djangoapps.course_overviews.models",
    ]

    for path in import_paths:
        try:
            module = __import__(path, fromlist=["CourseOverview"])
            return getattr(module, "CourseOverview")
        except (ImportError, AttributeError):
            continue

    raise ImportError("CourseOverview model not found in any known location")


def get_grades_model():
    """Dynamically import PersistentSubsectionGrade from available paths."""
    import_paths = [
        "lms.djangoapps.grades.models",
        "grades.models",
        "common.djangoapps.grades.models",
        "openedx.core.djangoapps.grades.models",
    ]

    for path in import_paths:
        try:
            module = __import__(path, fromlist=["PersistentSubsectionGrade"])
            return getattr(module, "PersistentSubsectionGrade")
        except (ImportError, AttributeError):
            continue

    return None


# Initialize models
CourseEnrollment = get_course_enrollment_model()
CourseOverview = get_course_overview_model()
PersistentSubsectionGrade = get_grades_model()


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
        """
        params = self.request.query_params
        user_id = params.get("user_id")
        if user_id is None:
            user_id = self.request.user.id
        else:
            user_id = int(user_id)

        return CourseEnrollment.objects.filter(user_id=user_id)

    def list(self, request, *args, **kwargs):
        # Apply filters and paginate
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        objects = page if page is not None else queryset

        # Collect course_ids visible on this page
        course_ids = [str(e.course_id) for e in objects]

        # Get course titles
        titles = {}
        if course_ids:
            try:
                titles = {
                    str(rec["id"]): rec["display_name"]
                    for rec in CourseOverview.objects.filter(id__in=course_ids).values(
                        "id", "display_name"
                    )
                }
            except Exception as e:
                # Log the error but continue
                print(f"Error fetching course titles: {e}")
                titles = {}

        # Get graded subsections count
        graded_counts = {}
        if PersistentSubsectionGrade and course_ids:
            try:
                user_id = request.query_params.get("user_id") or request.user.id
                agg = (
                    PersistentSubsectionGrade.objects.filter(
                        user_id=user_id, course_id__in=course_ids
                    )
                    .filter(possible_graded__gt=0)
                    .values("course_id")
                    .annotate(count=Count("id"))
                )
                graded_counts = {
                    str(row["course_id"]): int(row["count"]) for row in agg
                }
            except Exception as e:
                print(f"Error fetching graded counts: {e}")
                graded_counts = {}

        # Serialize
        serializer = self.get_serializer(
            objects,
            many=True,
            context={"course_titles": titles, "graded_counts": graded_counts},
        )

        if page is not None:
            response = self.get_paginated_response(serializer.data)
        else:
            response = Response(serializer.data)

        response["Cache-Control"] = "public, max-age=300"
        return response
