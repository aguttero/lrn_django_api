"""
Tests for models.
"""

# tool to mock things (behaviour)
from unittest.mock import patch

# fetches the default user model for the project:
from decimal import Decimal  # for values in recipe model

from django.contrib.auth import get_user_model  # to test user model
from django.test import TestCase

from core import models  # to test recipe model


def create_user(email='user@example.com', password='testpass123'):
    """Create a return a new user."""
    return get_user_model().objects.create_user(email, password)

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

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        # [input_email, expected_after_normalized_email]
        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.com", "TEST3@example.com"],
            ["test4@example.COM", "test4@example.com"],
        ]
        for email, expected in sample_emails:
            # password is fixed to "sample123" as we are not testing it here
            # but password is requested to create user
            user = get_user_model().objects.create_user(email, "sample123")
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            # create a user with a blank email address
            get_user_model().objects.create_user("", "test123")

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            "test@example.com",
            "test123",
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test creating a recipe is successful."""
        # need a user to assing the recipe to
        user = get_user_model().objects.create_user(
            "test@example.com",
            "testpass123",
        )
        recipe = models.Recipe.objects.create(
            user=user, # user created above
            title="Sample recipe name",
            time_minutes=5,
            price=Decimal("5.50"),
            description="Sample receipe description.",
        )

        # validates the string representation of the model instance
        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test creating a tag is successful."""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='Tag1')

        # Validates tag was create and that name matches
        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """Test creating an ingredient is successful."""
        user = create_user()
        ingredient = models.Ingredient.objects.create(
            user=user,
            name='Ingredient1'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    # uuid for filename(unique identifier)
    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test generating image path."""
        # this is the mock response -> 'test-uuid'
        uuid = 'test-uuid'
        # here we assign the mocked return value
        mock_uuid.return_value = uuid
        # this is the function that generates the path to the image
        # that is being uploaded. None replaces the instance parameter
        file_path = models.recipe_image_file_path(None, 'example.jpg')

        # test that the paths matches
        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')
