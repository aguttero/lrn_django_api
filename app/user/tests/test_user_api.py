"""
Tests for the user API.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

# from user/urls.py app_name="user" 'create' endpoint (urlpatterns)
CREATE_USER_URL = reverse("user:create")


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


# TEST DB gets erased after each single test
# Public: tests for features that don't require authentication


class PublicUserApiTests(TestCase):
    """Test the public features of the user API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user is successful."""
        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test Name",
        }
        # POST to CREATE_USER_URL and pass payload
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))
        # validate we are not returning password data in the response
        # there is not key 'password' in the response
        self.assertNotIn("password", res.data)

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists."""
        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test Name",
        }
        # ZAG payload2 used to verify that DB User table is reset each time each def_test is run
        payload2 = {
            "email": "test2@example.com",
            "password": "testpass123",
            "name": "Test Name 2",
        }
        create_user(**payload)
        # res = self.client.post(CREATE_USER_URL, payload2)
        res = self.client.post(CREATE_USER_URL, payload)
        # After sendin req to create a new user with an email
        # that already exists in the DB we should receice a 400 error
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password less than 5 chars."""
        payload = {
            "email": "test@example.com",
            "password": "pw",
            "name": "Test name",
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # Also need to validate that the user was not created in the DB
        user_exists = get_user_model().objects.filter(email=payload["email"]).exists()
        self.assertFalse(user_exists)
