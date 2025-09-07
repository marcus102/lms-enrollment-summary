"""
Tests for the Enrollment Summary API services.
"""

from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from common.djangoapps.student.models import CourseEnrollment
from opaque_keys.edx.keys import CourseKey

from enrollment_summary_api.services import EnrollmentSummaryService

User = get_user_model()


class EnrollmentSummaryServiceTestCase(TestCase):
    """Test cases for the EnrollmentSummaryService."""
    
    def setUp(self):
        """Set up test data."""
        cache.clear()
        
        self.service = EnrollmentSummaryService()
        
        # Create test user
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test course keys
        self.course_key = CourseKey.from_string('course-v1:TestX+CS101+2023')
        
        # Create test enrollment
        self.enrollment = CourseEnrollment.objects.create(
            user=self.test_user,
            course_id=self.course_key,
            is_active=True
        )
    
    @patch('enrollment_summary_api.services.EnrollmentSummaryService._get_course_overviews')
    @patch('enrollment_summary_api.services.EnrollmentSummaryService._get_graded_subsections_count')
    def test_get_enrollment_summaries_basic(self, mock_graded_count, mock_overviews):
        """Test basic enrollment summary retrieval."""
        # Mock dependencies
        mock_overviews.return_value = {
            str(self.course_key): {
                'display_name': 'Test Course',
                'start': None,
                'end': None,
            }
        }
        mock_graded_count.return_value = 5
        
        summaries = self.service.get_enrollment_summaries()
        
        self.assertEqual(len(summaries), 1)
        summary = summaries[0]
        
        self.assertEqual(summary['user_id'], self.test_user.id)
        self.assertEqual(summary['username'], self.test_user.username)
        self.assertEqual(summary['course_key'], str(self.course_key))
        self.assertEqual(summary['course_title'], 'Test Course')
        self.assertEqual(summary['enrollment_status'], 'active')
        self.assertTrue(summary['is_active'])
        self.assertEqual(summary['graded_subsections_count'], 5)
    
    @patch('enrollment_summary_api.services.EnrollmentSummaryService._get_course_overviews')
    @patch('enrollment_summary_api.services.EnrollmentSummaryService._get_graded_subsections_count')
    def test_get_enrollment_summaries_with_user_filter(self, mock_graded_count, mock_overviews):
        """Test enrollment summary retrieval with user filter."""
        # Create another user and enrollment
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        CourseEnrollment.objects.create(
            user=other_user,
            course_id=self.course_key,
            is_active=True
        )
        
        mock_overviews.return_value = {str(self.course_key): {'display_name': 'Test Course', 'start': None, 'end': None}}
        mock_graded_count.return_value = 0
        
        # Filter by specific user
        summaries = self.service.get_enrollment_summaries(user_id=self.test_user.id)
        
        self.assertEqual(len(summaries), 1)
        self.assertEqual(summaries[0]['user_id'], self.test_user.id)
    
    @patch('enrollment_summary_api.services.EnrollmentSummaryService._get_course_overviews')
    @patch('enrollment_summary_api.services.EnrollmentSummaryService._get_graded_subsections_count')
    def test_get_enrollment_summaries_with_active_filter(self, mock_graded_count, mock_overviews):
        """Test enrollment summary retrieval with active filter."""
        # Create inactive enrollment
        CourseEnrollment.objects.create(
            user=self.test_user,
            course_id=CourseKey.from_string('course-v1:TestX+CS102+2023'),
            is_active=False
        )
        
        mock_overviews.return_value = {}
        mock_graded_count.return_value = 0
        
        # Filter by active enrollments only
        summaries = self.service.get_enrollment_summaries(active=True)
        
        self.assertEqual(len(summaries), 1)
        self.assertTrue(summaries[0]['is_active'])
        
        # Filter by inactive enrollments only
        summaries = self.service.get_enrollment_summaries(active=False)
        
        self.assertEqual(len(summaries), 1)
        self.assertFalse(summaries[0]['is_active'])
    
    def test_build_cache_key(self):
        """Test cache key building."""
        # Test basic cache key
        key = self.service._build_cache_key(None, None, None)
        self.assertEqual(key, 'enrollment_summaries')
        
        # Test with user_id
        key = self.service._build_cache_key(123, None, None)
        self.assertEqual(key, 'enrollment_summaries:user_123')
        
        # Test with all parameters
        key = self.service._build_cache_key(123, True, 'course-v1:TestX+CS101+2023')
        expected = 'enrollment_summaries:user_123:active_True:course_course-v1_TestX_CS101_2023'
        self.assertEqual(key, expected)
    
    def test_get_enrollment_status(self):
        """Test enrollment status determination."""
        # Test active enrollment
        status = self.service._get_enrollment_status(self.enrollment)
        self.assertEqual(status, 'active')
        
        # Test inactive enrollment
        self.enrollment.is_active = False
        status = self.service._get_enrollment_status(self.enrollment)
        self.assertEqual(status, 'inactive')