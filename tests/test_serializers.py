"""
Tests for LMS Enrollment Summary serializers
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from datetime import datetime

from student.models import CourseEnrollment
from opaque_keys.edx.keys import CourseKey
from lms_enrollment_summary.serializers import EnrollmentSummarySerializer

User = get_user_model()


class EnrollmentSummarySerializerTestCase(TestCase):
    """
    Test cases for EnrollmentSummarySerializer
    """
    
    def setUp(self):
        """
        Set up test data
        """
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        
        self.course_key = CourseKey.from_string('course-v1:TestOrg+CS101+2023_Fall')
        
        self.enrollment = CourseEnrollment.objects.create(
            user=self.user,
            course_id=self.course_key,
            mode='audit',
            is_active=True
        )
    
    @patch('lms_enrollment_summary.serializers.CourseOverview.objects.get')
    def test_serialization_with_course_overview(self, mock_course_overview):
        """
        Test serialization when CourseOverview exists
        """
        # Mock CourseOverview
        mock_overview = MagicMock()
        mock_overview.id = self.course_key
        mock_overview.display_name = 'Test Course'
        mock_course_overview.return_value = mock_overview
        
        serializer = EnrollmentSummarySerializer()
        
        with patch.object(serializer, '_get_graded_subsections_count', return_value=5):
            result = serializer.to_representation(self.enrollment)
        
        expected_data = {
            'user_id': self.user.id,
            'username': self.user.username,
            'course_key': str(self.course_key),
            'course_title': 'Test Course',
            'enrollment_status': 'audit',
            'is_active': True,
            'enrollment_date': self.enrollment.created,
            'graded_subsections_count': 5,
        }
        
        self.assertEqual(result, expected_data)
    
    @patch('lms_enrollment_summary.serializers.CourseOverview.objects.get')
    def test_serialization_without_course_overview(self, mock_course_overview):
        """
        Test serialization when CourseOverview doesn't exist
        """
        from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
        mock_course_overview.side_effect = CourseOverview.DoesNotExist()
        
        serializer = EnrollmentSummarySerializer()
        result = serializer.to_representation(self.enrollment)
        
        self.assertEqual(result['course_title'], 'Unknown Course')
        self.assertEqual(result['graded_subsections_count'], 0)
    
    def test_graded_subsections_count_calculation(self):
        """
        Test graded subsections count calculation
        """
        serializer = EnrollmentSummarySerializer()
        
        # Mock course overview
        mock_overview = MagicMock()
        mock_overview.id = self.course_key
        
        # Test with modulestore available
        with patch('lms_enrollment_summary.serializers.modulestore') as mock_modulestore:
            # Mock course structure
            mock_course = MagicMock()
            mock_chapter = MagicMock()
            mock_graded_section = MagicMock()
            mock_graded_section.graded = True
            mock_ungraded_section = MagicMock()
            mock_ungraded_section.graded = False
            
            mock_chapter.get_children.return_value = [mock_graded_section, mock_ungraded_section]
            mock_course.get_children.return_value = [mock_chapter]
            
            mock_modulestore.return_value.get_course.return_value = mock_course
            
            count = serializer._get_graded_subsections_count(mock_overview)
            self.assertEqual(count, 1)
        
        # Test with modulestore exception
        with patch('lms_enrollment_summary.serializers.modulestore') as mock_modulestore:
            mock_modulestore.return_value.get_course.side_effect = Exception("Modulestore error")
            count = serializer._get_graded_subsections_count(mock_overview)
            self.assertEqual(count, 0)