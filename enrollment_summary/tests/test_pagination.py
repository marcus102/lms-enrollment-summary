import pytest
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from enrollment_summary.pagination import StandardResultsSetPagination

@pytest.mark.parametrize(
    "page_size, expected_len",
    [(None, 20), (10, 10), (50, 50)]
)
def test_standard_pagination_page_sizes(page_size, expected_len):
    items = list(range(0, 100))  # a simple list works fine

    rf = APIRequestFactory()
    params = {}
    if page_size is not None:
        params["page_size"] = str(page_size)
    request = Request(rf.get("/api/enrollments/summary", params))

    paginator = StandardResultsSetPagination()
    page = paginator.paginate_queryset(items, request)
    assert len(page) == expected_len
