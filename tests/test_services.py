"""
Tests for the Enrollment Summary API serializers.
"""

from django.test import TestCase
from datetime import datetime, timezone
from enrollment_summary.serializers import EnrollmentSummarySerializer


class EnrollmentSummarySerializerTestCase(TestCase):
    """Test cases for the EnrollmentSummarySerializer."""
    
    def test_serializer_with_valid_data(self):
        """Test serializer with valid enrollment data."""
        data = {
            'user_id': 123,
            'username': 'testuser',
            'course_key': 'course-v1:TestX+CS101+2023',
            'course_title': 'Introduction to Computer Science',
            'enrollment_status': 'active',
            'is_active': True,
            'enrollment_date': datetime(2023, 9, 1, tzinfo=timezone.utc),
            'graded_subsections_count': 5,
            'course_start': datetime(2023, 9, 15, tzinfo=timezone.utc),
            'course_end': datetime(2023, 12, 15, tzinfo=timezone.utc),
        }
        
        serializer = EnrollmentSummarySerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        validated_data = serializer.validated_data
        self.assertEqual(validated_data['user_id'], 123)
        self.assertEqual(validated_data['username'], 'testuser')
        self.assertEqual(validated_data['course_key'], 'course-v1:TestX+CS101+2023')
        self.assertEqual(validated_data['graded_subsections_count'], 5)
    
    def test_serializer_with_minimal_data(self):
        """Test serializer with minimal required data."""
        data = {
            'user_id': 123,
            'username': 'testuser',
            'course_key': 'course-v1:TestX+CS101+2023',
            'course_title': '',
            'enrollment_status': 'active',
            'is_active': True,
            'enrollment_date': datetime(2023, 9, 1, tzinfo=timezone.utc),
        }
        
        serializer = EnrollmentSummarySerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        # Test default values
        validated_data = serializer.validated_data
        self.assertEqual(validated_data['graded_subsections_count'], 0)
    
    def test_serializer_output(self):
        """Test serializer output format."""
        data = {
            'user_id': 123,
            'username': 'testuser',
            'course_key': 'course-v1:TestX+CS101+2023',
            'course_title': 'Test Course',
            'enrollment_status': 'active',
            'is_active': True,
            'enrollment_date': datetime(2023, 9, 1, tzinfo=timezone.utc),
            'graded_subsections_count': 3,
            'course_start': None,
            'course_end': None,
        }
        
        serializer = EnrollmentSummarySerializer(data)
        output = serializer.data
        
        self.assertIn('user_id', output)
        self.assertIn('username', output)
        self.assertIn('course_key', output)
        self.assertIn('course_title', output)
        self.assertIn('enrollment_status', output)
        self.assertIn('is_active', output)
        self.assertIn('enrollment_date', output)
        self.assertIn('graded_subsections_count', output)
        self.assertIn('course_start', output)
        self.assertIn('course_end', output)