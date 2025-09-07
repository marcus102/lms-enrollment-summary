"""
Tests for the Enrollment Summary API views.
"""

import json
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from common.djangoapps.student.models import CourseEnrollment
from opaque_keys.edx.keys import CourseKey

User = get_user_model()


class EnrollmentSummaryAPITestCase(TestCase):
    """Test cases for the Enrollment Summary API."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test users
        self.staff_user = User.objects.create_user(
            username='staff_user',
            email='staff@example.com',
            password='testpass123',
            is_staff=True
        )
        
        self.regular_user = User.objects.create_user(
            username='regular_user',
            email='regular@example.com',
            password='testpass123'
        )
        
        self.student_user = User.objects.create_user(
            username='student_user',
            email='student@example.com',
            password='testpass123'
        )
        
        # Create test course keys
        self.course_key1 = CourseKey.from_string('course-v1:TestX+CS101+2023')
        self.course_key2 = CourseKey.from_string('course-v1:TestX+CS102+2023')
        
        # Create test enrollments
        self.enrollment1 = CourseEnrollment.objects.create(
            user=self.student_user,
            course_id=self.course_key1,
            is_active=True
        )
        
        self.enrollment2 = CourseEnrollment.objects.create(
            user=self.student_user,
            course_id=self.course_key2,
            is_active=False
        )
        
        self.url = reverse('enrollment_summary_api:enrollment-summary-list')
    
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access the API."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_non_staff_access_denied(self):
        """Test that non-staff users cannot access the API."""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    @patch('enrollment_summary_api.services.EnrollmentSummaryService.get_enrollment_summaries')
    def test_staff_can_access_api(self, mock_service):
        """Test that staff users can access the API."""
        mock_service.return_value = []
        
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_service.assert_called_once()
    
    @patch('enrollment_summary_api.services.EnrollmentSummaryService.get_enrollment_summaries')
    def test_filter_by_user_id(self, mock_service):
        """Test filtering by user_id parameter."""
        mock_service.return_value = []
        
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(f'{self.url}?user_id={self.student_user.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_service.assert_called_once_with(user_id=self.student_user.id)
    
    def test_invalid_user_id(self):
        """Test handling of invalid user_id parameter."""
        self.client.force_authenticate(user=self.staff_user)
        
        # Test non-integer user_id
        response = self.client.get(f'{self.url}?user_id=invalid')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test non-existent user_id
        response = self.client.get(f'{self.url}?user_id=99999')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    @patch('enrollment_summary_api.services.EnrollmentSummaryService.get_enrollment_summaries')
    def test_filter_by_active_status(self, mock_service):
        """Test filtering by active status."""
        mock_service.return_value = []
        
        self.client.force_authenticate(user=self.staff_user)
        
        # Test active=true
        response = self.client.get(f'{self.url}?active=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_service.assert_called_with(active=True)
        
        # Test active=false
        mock_service.reset_mock()
        response = self.client.get(f'{self.url}?active=false')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_service.assert_called_with(active=False)
    
    def test_invalid_active_parameter(self):
        """Test handling of invalid active parameter."""
        self.client.force_authenticate(user=self.staff_user)
        
        response = self.client.get(f'{self.url}?active=invalid')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('enrollment_summary_api.services.EnrollmentSummaryService.get_enrollment_summaries')
    def test_filter_by_course_key(self, mock_service):
        """Test filtering by course_key parameter."""
        mock_service.return_value = []
        
        self.client.force_authenticate(user=self.staff_user)
        course_key_str = str(self.course_key1)
        response = self.client.get(f'{self.url}?course_key={course_key_str}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_service.assert_called_once_with(course_key=course_key_str)
    
    def test_invalid_course_key(self):
        """Test handling of invalid course_key parameter."""
        self.client.force_authenticate(user=self.staff_user)
        
        response = self.client.get(f'{self.url}?course_key=invalid-key')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)