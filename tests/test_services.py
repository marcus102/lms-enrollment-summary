"""
Tests for enrollment summary services
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch, MagicMock

from common.djangoapps.student.models import CourseEnrollment
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from opaque_keys.edx.keys import CourseKey

from enrollment_summary.services import EnrollmentSummaryService

User = get_user_model()


class EnrollmentSummaryServiceTest(TestCase):
    """Test cases for the EnrollmentSummaryService."""
    
    def setUp(self):
        """Set up test data."""
        self.service = EnrollmentSummaryService()
        
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='user1@example.com'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='user2@example.com'
        )
        
        # Create test course keys
        self.course_key1 = CourseKey.from_string('course-v1:TestX+CS101+2023')
        self.course_key2 = CourseKey.from_string('course-v1:TestX+CS102+2023')
        
        # Create test enrollments
        self.enrollment1 = CourseEnrollment.objects.create(
            user=self.user1,
            course_id=self.course_key1,
            mode='audit',
            is_active=True
        )
        
        self.enrollment2 = CourseEnrollment.objects.create(
            user=self.user2,
            course_id=self.course_key2,
            mode='verified',
            is_active=False
        )
    
    @patch('enrollment_summary_api.services.CourseOverview.objects.get')
    @patch('enrollment_summary_api.services.EnrollmentSummaryService._count_graded_subsections')
    def test_get_all_enrollments(self, mock_count_graded, mock_get_overview):
        """Test getting all enrollment summaries without filters."""
        # Mock course overview
        mock_overview = MagicMock()
        mock_overview.display_name = 'Test Course'
        mock_overview.short_description = 'A test course'
        mock_overview.start = None
        mock_overview.end = None
        mock_get_overview.return_value = mock_overview
        
        # Mock graded subsections count
        mock_count_graded.return_value = 5
        
        summaries = self.service.get_enrollment_summaries()
        
        self.assertEqual(len(summaries), 2)
        
        # Verify the structure
        summary = summaries[0]  # Most recent first
        self.assertIn('user_id', summary)
        self.assertIn('username', summary)
        self.assertIn('course_key', summary)
        self.assertIn('enrollment_status', summary)
        self.assertIn('graded_subsections_count', summary)
    
    @patch('enrollment_summary_api.services.CourseOverview.objects.get')
    @patch('enrollment_summary_api.services.EnrollmentSummaryService._count_graded_subsections')
    def test_filter_by_user_id(self, mock_count_graded, mock_get_overview):
        """Test filtering enrollments by user ID."""
        mock_overview = MagicMock()
        mock_overview.display_name = 'Test Course'
        mock_overview.short_description = 'A test course'
        mock_overview.start = None
        mock_overview.end = None
        mock_get_overview.return_value = mock_overview
        mock_count_graded.return_value = 3
        
        summaries = self.service.get_enrollment_summaries(user_id=self.user1.id)
        
        self.assertEqual(len(summaries), 1)
        self.assertEqual(summaries[0]['user_id'], self.user1.id)
    
    @patch('enrollment_summary_api.services.CourseOverview.objects.get')
    @patch('enrollment_summary_api.services.EnrollmentSummaryService._count_graded_subsections')
    def test_filter_by_active_status(self, mock_count_graded, mock_get_overview):
        """Test filtering enrollments by active status."""
        mock_overview = MagicMock()
        mock_overview.display_name = 'Test Course'
        mock_overview.short_description = 'A test course'
        mock_overview.start = None
        mock_overview.end = None
        mock_get_overview.return_value = mock_overview
        mock_count_graded.return_value = 3
        
        # Test active enrollments
        active_summaries = self.service.get_enrollment_summaries(active=True)
        self.assertEqual(len(active_summaries), 1)
        self.assertTrue(active_summaries[0]['is_active'])
        
        # Test inactive enrollments
        inactive_summaries = self.service.get_enrollment_summaries(active=False)
        self.assertEqual(len(inactive_summaries), 1)
        self.assertFalse(inactive_summaries[0]['is_active'])
    
    @patch('enrollment_summary_api.services.modulestore')
    def test_count_graded_subsections(self, mock_modulestore):
        """Test counting graded subsections in a course."""
        # Mock course structure
        mock_store = MagicMock()
        mock_modulestore.return_value = mock_store
        
        # Mock course with chapters and subsections
        mock_course = MagicMock()
        mock_course.children = ['chapter1', 'chapter2']
        mock_store.get_course.return_value = mock_course
        
        # Mock chapters
        mock_chapter1 = MagicMock()
        mock_chapter1.children = ['subsection1', 'subsection2']
        mock_chapter2 = MagicMock()
        mock_chapter2.children = ['subsection3']
        
        # Mock subsections (first two are graded, last is not)
        mock_subsection1 = MagicMock()
        mock_subsection1.graded = True
        mock_subsection2 = MagicMock()
        mock_subsection2.graded = True
        mock_subsection3 = MagicMock()
        mock_subsection3.graded = False
        
        # Set up the store to return the right objects
        def get_item_side_effect(key):
            if key == 'chapter1':
                return mock_chapter1
            elif key == 'chapter2':
                return mock_chapter2
            elif key == 'subsection1':
                return mock_subsection1
            elif key == 'subsection2':
                return mock_subsection2
            elif key == 'subsection3':
                return mock_subsection3
            return None
        
        mock_store.get_item.side_effect = get_item_side_effect
        
        count = self.service._count_graded_subsections(self.course_key1)
        self.assertEqual(count, 2)  # Only two subsections are graded