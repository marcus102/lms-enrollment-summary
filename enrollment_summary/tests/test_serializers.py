from django.test import TestCase
from enrollment_summary.serializers import EnrollmentSummarySerializer
from datetime import datetime


class EnrollmentSummarySerializerTest(TestCase):
    """
    Test cases for EnrollmentSummarySerializer.
    """
    
    def test_serialization(self):
        """Test serialization of enrollment summary data."""
        data = {
            'user_id': 1,
            'username': 'testuser',
            'course_key': 'course-v1:TestOrg+Test101+2024',
            'course_title': 'Test Course',
            'enrollment_status': 'verified',
            'is_active': True,
            'created': datetime.now(),
            'graded_subsections_count': 5
        }
        
        serializer = EnrollmentSummarySerializer(data)
        serialized_data = serializer.data
        
        self.assertEqual(serialized_data['user_id'], 1)
        self.assertEqual(serialized_data['username'], 'testuser')
        self.assertEqual(serialized_data['course_key'], 'course-v1:TestOrg+Test101+2024')
        self.assertEqual(serialized_data['course_title'], 'Test Course')
        self.assertEqual(serialized_data['enrollment_status'], 'verified')
        self.assertTrue(serialized_data['is_active'])
        self.assertEqual(serialized_data['graded_subsections_count'], 5)
    
    def test_multiple_items_serialization(self):
        """Test serialization of multiple enrollment summaries."""
        data = [
            {
                'user_id': 1,
                'username': 'user1',
                'course_key': 'course-v1:TestOrg+Test101+2024',
                'course_title': 'Test Course 1',
                'enrollment_status': 'verified',
                'is_active': True,
                'created': datetime.now(),
                'graded_subsections_count': 3
            },
            {
                'user_id': 2,
                'username': 'user2',
                'course_key': 'course-v1:TestOrg+Test102+2024',
                'course_title': 'Test Course 2',
                'enrollment_status': 'audit',
                'is_active': False,
                'created': datetime.now(),
                'graded_subsections_count': 5
            }
        ]
        
        serializer = EnrollmentSummarySerializer(data, many=True)
        serialized_data = serializer.data
        
        self.assertEqual(len(serialized_data), 2)
        self.assertEqual(serialized_data[0]['user_id'], 1)
        self.assertEqual(serialized_data[1]['user_id'], 2)
