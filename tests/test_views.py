"""
Tests for enrollment summary API views
"""
import json
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock

from common.djangoapps.student.models import CourseEnrollment
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from opaque_keys.edx.keys import CourseKey

User = get_user_model()


class EnrollmentSummaryAPIViewTest(TestCase):
    """Test cases for the EnrollmentSummaryAPIView."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test users
        self.staff_user = User.objects.create_user(
            username='staff_user',
            email='staff@example.com',
            password='testpass',
            is_staff=True
        )
        
        self.regular_user = User.objects.create_user(
            username='regular_user',
            email='user@example.com',
            password='testpass'
        )
        
        self.student_user = User.objects.create_user(
            username='student_user',
            email='student@example.com',
            password='testpass'
        )
        
        # Create test course key
        self.course_key = CourseKey.from_string('course-v1:TestX+CS101+2023')
        
        # Mock CourseOverview
        self.course_overview = MagicMock()
        self.course_overview.id = self.course_key
        self.course_overview.display_name = 'Test Course'
        self.course_overview.short_description = 'A test course'
        self.course_overview.start = None
        self.course_overview.end = None
        
        # Create test enrollment
        self.enrollment = CourseEnrollment.objects.create(
            user=self.student_user,
            course_id=self.course_key,
            mode='audit',
            is_active=True
        )
        
        self.url = reverse('enrollment_summary_api:enrollment-summary')
    
    def test_unauthenticated_request(self):
        """Test that unauthenticated requests are rejected."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_non_staff_request(self):
        """Test that non-staff users are rejected."""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    @patch('enrollment_summary_api.services.EnrollmentSummaryService.get_enrollment_summaries')
    def test_staff_request_success(self, mock_get_summaries):
        """Test successful request by staff user."""
        # Mock the service response
        mock_get_summaries.return_value = [
            {
                'user_id': self.student_user.id,
                'username': self.student_user.username,
                'course_key': str(self.course_key),
                'course_title': 'Test Course',
                'course_short_description': 'A test course',
                'enrollment_status': 'active',
                'enrollment_mode': 'audit',
                'is_active': True,
                'created_date': self.enrollment.created,
                'graded_subsections_count': 5,
                'course_start': None,
                'course_end': None,
            }
        ]
        
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        
        # Verify the structure of returned data
        result = response.data['results'][0]
        self.assertEqual(result['user_id'], self.student_user.id)
        self.assertEqual(result['course_key'], str(self.course_key))
        self.assertEqual(result['enrollment_status'], 'active')
    
    def test_invalid_user_id_parameter(self):
        """Test handling of invalid user_id parameter."""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(self.url, {'user_id': 'invalid'})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('valid integer', response.data['error'])
    
    def test_nonexistent_user_id(self):
        """Test handling of nonexistent user ID."""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(self.url, {'user_id': 99999})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('does not exist', response.data['error'])
    
    def test_invalid_active_parameter(self):
        """Test handling of invalid active parameter."""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(self.url, {'active': 'invalid'})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('true or false', response.data['error'])
    
    @patch('enrollment_summary_api.services.EnrollmentSummaryService.get_enrollment_summaries')
    def test_filtering_by_user_id(self, mock_get_summaries):
        """Test filtering by user_id parameter."""
        mock_get_summaries.return_value = []
        
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(self.url, {'user_id': self.student_user.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get_summaries.assert_called_once_with(
            user_id=self.student_user.id,
            active=None
        )
    
    @patch('enrollment_summary_api.services.EnrollmentSummaryService.get_enrollment_summaries')
    def test_filtering_by_active_status(self, mock_get_summaries):
        """Test filtering by active parameter."""
        mock_get_summaries.return_value = []
        
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(self.url, {'active': 'true'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get_summaries.assert_called_once_with(
            user_id=None,
            active=True
        )