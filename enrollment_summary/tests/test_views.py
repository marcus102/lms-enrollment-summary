import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_enrollment_summary_view(user_factory, course_factory, enrollment_factory):
    user = user_factory()
    course = course_factory()
    enrollment_factory(user=user, course=course, is_active=True)

    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse("enrollment_summary:summary")
    response = client.get(url, {"user_id": user.id, "active": True})

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert data["results"][0]["course_key"] == str(course.id)
