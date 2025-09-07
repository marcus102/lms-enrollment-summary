"""
Tests for enrollment summary serializers
"""
from django.test import TestCase
from datetime import datetime
from django.utils import timezone

from enrollment_summary.serializers import EnrollmentSummarySerializer


class EnrollmentSummarySerializerTest(TestCase):
    """Test cases for the EnrollmentSummarySerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.valid_data = {
            'user_id': 123,
            'username': 'testuser',
            'course_key': 'course-v1:TestX+CS101+2023',
            'course_title': 'Introduction to Computer Science',
            'course_short_description': 'Learn the basics of computer science',
            'enrollment_status': 'active',
            'enrollment_mode': 'audit',
            'is_active': True,
            'created_date': timezone.now(),
            'graded_subsections_count': 10,
            'course_start': timezone.now(),
            'course_end': timezone.now(),
        }
    
    def test_valid_serialization(self):
        """Test serialization of valid data."""
        serializer = EnrollmentSummarySerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        
        serialized_data = serializer.validated_data
        self.assertEqual(serialized_data['user_id'], 123)
        self.assertEqual(serialized_data['username'], 'testuser')
        self.assertEqual(serialized_data['course_key'], 'course-v1:TestX+CS101+2023')
    
    def test_missing_required_fields(self):
        """Test validation with missing required fields."""
        incomplete_data = self.valid_data.copy()
        del incomplete_data['course_key']
        del incomplete_data['user_id']
        
        serializer = EnrollmentSummarySerializer(data=incomplete_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('course_key', str(serializer.errors))
        self.assertIn('user_id', str(serializer.errors))
    
    def test_nullable_fields(self):
        """Test that nullable fields can be None."""
        data_with_nulls = self.valid_data.copy()
        data_with_nulls.update({
            'course_title': None,
            'course_short_description': None,
            'course_start': None,
            'course_end': None,
        })
        
        serializer = EnrollmentSummarySerializer(data=data_with_nulls)
        self.assertTrue(serializer.is_valid())