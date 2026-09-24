"""
Tests for models.
"""

#fetches the default user model for the project:
from django.contrib.auth import get_user_model

from django.test import TestCase


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        # example.com is a reserved domain for testing
        # best practice to use this to avoid sending test emails
        # to actual users
        email = "test@example.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
