from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from student.models import CourseEnrollment
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from opaque_keys.edx.keys import CourseKey
from unittest.mock import patch, Mock


class EnrollmentSummaryAPITest(APITestCase):
    """
    Test cases for the Enrollment Summary API.
    """
    
    def setUp(self):
        """Set up test data."""
        # Create test users
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass',
            is_staff=True,
            is_superuser=True
        )
        
        self.regular_user = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='testpass'
        )
        
        self.test_user = User.objects.create_user(
            username='testuser',
            email='testuser@test.com',
            password='testpass'
        )
        
        # Create test course key
        self.course_key = CourseKey.from_string('course-v1:TestOrg+Test101+2024')
        
        # Create test course overview
        self.course_overview = CourseOverview.objects.create(
            id=self.course_key,
            display_name='Test Course 101',
            start=None,
            end=None
        )
        
        # Create test enrollment
        self.enrollment = CourseEnrollment.objects.create(
            user=self.test_user,
            course_id=self.course_key,
            mode='verified',
            is_active=True
        )
        
        self.url = reverse('enrollment_summary:enrollment-summary-list')
    
    def test_unauthorized_access(self):
        """Test that unauthorized users cannot access the API."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_non_staff_access(self):
        """Test that non-staff users cannot access the API."""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    @patch('enrollment_summary.services.EnrollmentSummaryService._get_graded_subsections_count')
    def test_successful_request(self, mock_graded_count):
        """Test successful API request."""
        mock_graded_count.return_value = 5
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertIn('page', response.data)
        self.assertIn('page_size', response.data)
        
        # Check that we have at least one result
        self.assertGreaterEqual(response.data['count'], 1)
        
        # Check the structure of the first result
        if response.data['results']:
            result = response.data['results'][0]
            expected_fields = [
                'user_id', 'username', 'course_key', 'course_title',
                'enrollment_status', 'is_active', 'created', 'graded_subsections_count'
            ]
            for field in expected_fields:
                self.assertIn(field, result)
    
    @patch('enrollment_summary.services.EnrollmentSummaryService._get_graded_subsections_count')
    def test_user_id_filter(self, mock_graded_count):
        """Test filtering by user_id."""
        mock_graded_count.return_value = 3
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'{self.url}?user_id={self.test_user.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['user_id'], self.test_user.id)
    
    def test_invalid_user_id(self):
        """Test invalid user_id parameter."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'{self.url}?user_id=invalid')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_nonexistent_user_id(self):
        """Test nonexistent user_id parameter."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'{self.url}?user_id=99999')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    @patch('enrollment_summary.services.EnrollmentSummaryService._get_graded_subsections_count')
    def test_active_filter(self, mock_graded_count):
        """Test filtering by active status."""
        mock_graded_count.return_value = 2
        
        # Create inactive enrollment
        CourseEnrollment.objects.create(
            user=self.test_user,
            course_id=CourseKey.from_string('course-v1:TestOrg+Test102+2024'),
            mode='audit',
            is_active=False
        )
        
        self.client.force_authenticate(user=self.admin_user)
        
        # Test active=true
        response = self.client.get(f'{self.url}?active=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for result in response.data['results']:
            self.assertTrue(result['is_active'])
        
        # Test active=false
        response = self.client.get(f'{self.url}?active=false')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for result in response.data['results']:
            self.assertFalse(result['is_active'])
    
    def test_invalid_active_filter(self):
        """Test invalid active parameter."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'{self.url}?active=maybe')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    @patch('enrollment_summary.services.EnrollmentSummaryService._get_graded_subsections_count')
    def test_pagination(self, mock_graded_count):
        """Test pagination functionality."""
        mock_graded_count.return_value = 1
        
        # Create multiple enrollments
        for i in range(5):
            user = User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@test.com',
                password='testpass'
            )
            CourseEnrollment.objects.create(
                user=user,
                course_id=self.course_key,
                mode='audit',
                is_active=True
            )
        
        self.client.force_authenticate(user=self.admin_user)
        
        # Test first page
        response = self.client.get(f'{self.url}?page_size=3&page=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        self.assertEqual(response.data['page'], 1)
        self.assertIsNotNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        
        # Test second page
        response = self.client.get(f'{self.url}?page_size=3&page=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data['results']), 3)
        self.assertEqual(response.data['page'], 2)
        self.assertIsNotNone(response.data['previous'])