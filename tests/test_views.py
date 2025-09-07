"""
Tests for LMS Enrollment Summary views
"""
import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock

from student.models import CourseEnrollment
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from opaque_keys.edx.keys import CourseKey

User = get_user_model()


class EnrollmentSummaryViewTestCase(TestCase):
    """
    Test cases for EnrollmentSummaryViewSet
    """
    
    def setUp(self):
        """
        Set up test data
        """
        self.service = EnrollmentSummaryService()
        
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass'
        )
        
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass'
        )
        
        self.course_key_1 = CourseKey.from_string('course-v1:TestOrg+CS101+2023_Fall')
        self.course_key_2 = CourseKey.from_string('course-v1:TestOrg+CS102+2023_Fall')
        
        # Create test enrollments
        self.enrollment1 = CourseEnrollment.objects.create(
            user=self.user1,
            course_id=self.course_key_1,
            mode='audit',
            is_active=True
        )
        
        self.enrollment2 = CourseEnrollment.objects.create(
            user=self.user1,
            course_id=self.course_key_2,
            mode='verified',
            is_active=False
        )
        
        self.enrollment3 = CourseEnrollment.objects.create(
            user=self.user2,
            course_id=self.course_key_1,
            mode='audit',
            is_active=True
        )
    
    def test_get_enrollment_summary_no_filters(self):
        """
        Test getting all enrollment summaries without filters
        """
        result = self.service.get_enrollment_summary()
        self.assertEqual(result.count(), 3)
    
    def test_get_enrollment_summary_filter_by_user(self):
        """
        Test filtering by user_id
        """
        result = self.service.get_enrollment_summary(user_id=self.user1.id)
        self.assertEqual(result.count(), 2)
        
        for enrollment in result:
            self.assertEqual(enrollment.user_id, self.user1.id)
    
    def test_get_enrollment_summary_filter_by_active(self):
        """
        Test filtering by active status
        """
        result = self.service.get_enrollment_summary(active=True)
        self.assertEqual(result.count(), 2)
        
        for enrollment in result:
            self.assertTrue(enrollment.is_active)
    
    def test_get_enrollment_summary_filter_by_course(self):
        """
        Test filtering by course key
        """
        result = self.service.get_enrollment_summary(course_key=str(self.course_key_1))
        self.assertEqual(result.count(), 2)
        
        for enrollment in result:
            self.assertEqual(enrollment.course_id, self.course_key_1)
    
    def test_get_enrollment_summary_invalid_course_key(self):
        """
        Test handling invalid course key
        """
        result = self.service.get_enrollment_summary(course_key='invalid-key')
        self.assertEqual(result.count(), 0)
    
    def test_get_user_enrollment_stats(self):
        """
        Test getting user enrollment statistics
        """
        stats = self.service.get_user_enrollment_stats(self.user1.id)
        
        expected_stats = {
            'user_id': self.user1.id,
            'username': self.user1.username,
            'total_enrollments': 2,
            'active_enrollments': 1,
            'inactive_enrollments': 1,
        }
        
        self.assertEqual(stats, expected_stats)
    
    def test_get_user_enrollment_stats_nonexistent_user(self):
        """
        Test getting stats for non-existent user
        """
        stats = self.service.get_user_enrollment_stats(99999)
        self.assertIsNone(stats)