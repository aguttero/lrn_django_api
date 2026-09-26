"""
Tests for the Django admin modifications.
"""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


class AdminSiteTests(TestCase):
    """Tests for Django admin."""

    def setUp(self):
        """Create user and client."""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="testpass123",
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email="user@example.com", password="testpass123", name="Test User"
        )

    def test_users_lists(self):
        """Test that users are listed on page."""
        # list of users in the system
        url = reverse("admin:core_user_changelist")
        # http get using the force_login user (admin)
        res = self.client.get(url)

        # assert that page contains name of test user created
        # assert that page contains email of test user created
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """Test the edit user page works."""
        url = reverse('admin:core_user_change', args=[self.user.id])
        # args= is the user id number > admin/core/user/ID_NUMBER/change/
        res = self.client.get(url)

        # Assert that page loads ok (status_code = 200)
        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test the create user page works."""
        url = reverse('admin:core_user_add') # no args
        # no args as we are creating a new user
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
