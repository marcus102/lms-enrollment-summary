from django.test import TestCase
from django.contrib.auth.models import User
from django.core.cache import cache
from student.models import CourseEnrollment
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from opaque_keys.edx.keys import CourseKey
from enrollment_summary.services import EnrollmentSummaryService
from unittest.mock import patch, Mock


class EnrollmentSummaryServiceTest(TestCase):
    """
    Test cases for EnrollmentSummaryService.
    """
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        
        self.course_key = CourseKey.from_string('course-v1:TestOrg+Test101+2024')
        
        self.course_overview = CourseOverview.objects.create(
            id=self.course_key,
            display_name='Test Course',
            start=None,
            end=None
        )
        
        self.enrollment = CourseEnrollment.objects.create(
            user=self.user,
            course_id=self.course_key,
            mode='verified',
            is_active=True
        )
        
        # Clear cache before each test
        cache.clear()
    
    @patch('enrollment_summary.services.EnrollmentSummaryService._get_graded_subsections_count')
    def test_get_enrollment_summaries_success(self, mock_graded_count):
        """Test successful retrieval of enrollment summaries."""
        mock_graded_count.return_value = 4
        
        summaries, total_count = EnrollmentSummaryService.get_enrollment_summaries()
        
        self.assertEqual(total_count, 1)
        self.assertEqual(len(summaries), 1)
        
        summary = summaries[0]
        self.assertEqual(summary['user_id'], self.user.id)
        self.assertEqual(summary['username'], self.user.username)
        self.assertEqual(summary['course_key'], str(self.course_key))
        self.assertEqual(summary['course_title'], 'Test Course')
        self.assertEqual(summary['enrollment_status'], 'verified')
        self.assertTrue(summary['is_active'])
        self.assertEqual(summary['graded_subsections_count'], 4)
    
    @patch('enrollment_summary.services.EnrollmentSummaryService._get_graded_subsections_count')
    def test_user_id_filter(self, mock_graded_count):
        """Test filtering by user_id."""
        mock_graded_count.return_value = 2
        
        # Create another user and enrollment
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass'
        )
        CourseEnrollment.objects.create(
            user=other_user,
            course_id=self.course_key,
            mode='audit',
            is_active=True
        )
        
        # Filter by specific user
        summaries, total_count = EnrollmentSummaryService.get_enrollment_summaries(
            user_id=self.user.id
        )
        
        self.assertEqual(total_count, 1)
        self.assertEqual(summaries[0]['user_id'], self.user.id)
    
    @patch('enrollment_summary.services.EnrollmentSummaryService._get_graded_subsections_count')
    def test_active_filter(self, mock_graded_count):
        """Test filtering by active status."""
        mock_graded_count.return_value = 1
        
        # Create inactive enrollment
        CourseEnrollment.objects.create(
            user=self.user,
            course_id=CourseKey.from_string('course-v1:TestOrg+Test102+2024'),
            mode='audit',
            is_active=False
        )
        
        # Filter by active status
        summaries, total_count = EnrollmentSummaryService.get_enrollment_summaries(
            active=True
        )
        
        self.assertEqual(total_count, 1)
        self.assertTrue(summaries[0]['is_active'])
    
    @patch('enrollment_summary.services.EnrollmentSummaryService._get_graded_subsections_count')
    def test_pagination(self, mock_graded_count):
        """Test pagination functionality."""
        mock_graded_count.return_value = 3
        
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
        
        # Test first page
        summaries, total_count = EnrollmentSummaryService.get_enrollment_summaries(
            page_size=3, page=1
        )
        
        self.assertEqual(total_count, 6)  # Original + 5 new
        self.assertEqual(len(summaries), 3)
        
        # Test second page
        summaries, total_count = EnrollmentSummaryService.get_enrollment_summaries(
            page_size=3, page=2
        )
        
        self.assertEqual(total_count, 6)
        self.assertEqual(len(summaries), 3)
    
    @patch('enrollment_summary.services.modulestore')
    def test_graded_subsections_count_caching(self, mock_modulestore):
        """Test caching of graded subsections count."""
        # Mock course structure
        mock_sequential1 = Mock()
        mock_sequential1.graded = True
        mock_sequential2 = Mock()
        mock_sequential2.graded = False
        mock_sequential3 = Mock()
        mock_sequential3.graded = True
        
        mock_chapter = Mock()
        mock_chapter.get_children.return_value = [mock_sequential1, mock_sequential2, mock_sequential3]
        
        mock_course = Mock()
        mock_course.get_children.return_value = [mock_chapter]
        
        mock_store = Mock()
        mock_store.get_course.return_value = mock_course
        mock_modulestore.return_value = mock_store
        
        # First call should query the modulestore
        count = EnrollmentSummaryService._get_graded_subsections_count(self.course_key)
        self.assertEqual(count, 2)  # 2 graded subsections
        mock_store.get_course.assert_called_once_with(self.course_key)
        
        # Second call should use cache
        mock_store.reset_mock()
        count = EnrollmentSummaryService._get_graded_subsections_count(self.course_key)
        self.assertEqual(count, 2)
        mock_store.get_course.assert_not_called()