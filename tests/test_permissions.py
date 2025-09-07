"""
Tests for LMS Enrollment Summary permissions
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from unittest.mock import MagicMock

from lms_enrollment_summary.permissions import IsStaffOrSuperuser

User = get_user_model()


class IsStaffOrSuperuserTestCase(TestCase):
    """
    Test cases for IsStaffOrSuperuser permission
    """
    
    def setUp(self):
        """
        Set up test data
        """
        self.permission = IsStaffOrSuperuser()
        self.factory = APIRequestFactory()
        self.view = MagicMock()
        
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='testpass',
            is_staff=True
        )
        
        self.superuser = User.objects.create_user(
            username='superuser',
            email='superuser@example.com',
            password='testpass',
            is_superuser=True
        )
        
        self.regular_user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='testpass'
        )
    
    def test_staff_user_has_permission(self):
        """
        Test that staff users have permission
        """
        request = self.factory.get('/api/enrollments/summary/')
        request.user = self.staff_user
        
        self.assertTrue(self.permission.has_permission(request, self.view))
    
    def test_superuser_has_permission(self):
        """
        Test that superusers have permission
        """
        request = self.factory.get('/api/enrollments/summary/')
        request.user = self.superuser
        
        self.assertTrue(self.permission.has_permission(request, self.view))
    
    def test_regular_user_no_permission(self):
        """
        Test that regular users don't have permission
        """
        request = self.factory.get('/api/enrollments/summary/')
        request.user = self.regular_user
        
        self.assertFalse(self.permission.has_permission(request, self.view))
    
    def test_unauthenticated_user_no_permission(self):
        """
        Test that unauthenticated users don't have permission
        """
        request = self.factory.get('/api/enrollments/summary/')
        request.user = MagicMock()
        request.user.is_authenticated = False
        
        self.assertFalse(self.permission.has_permission(request, self.view))