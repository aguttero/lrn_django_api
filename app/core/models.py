"""
Database models.
"""
import uuid, os

from django.conf import settings # for field user in class Recipe

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models

# function that generates path to uploaded image
def recipe_image_file_path(instance, filename):
    """Generate file path for new recipe image."""
    # file extension
    ext = os.path.splitext(filename)[1]
    # create filename
    filename = f'{uuid.uuid4()}{ext}'
    # return path in the correct format for the server OS
    return os.path.join('uploads', 'recipe', filename)


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError("valid email address required")
        # user = self.model(email=email, **extra_fields)
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user

# we are not using standard base class models.Model here
# because we are extending the existing functionality of users
class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    # only staff users can login to django admin

    # this is how you assing a User Manager in django
    objects = UserManager()

    # this is what replaces the django default username field from
    # username to email
    USERNAME_FIELD = "email"

# here we use the Base class provided by django
# on_delete=CASCADE if user is deleted all recipes are deleted
class Recipe(models.Model):
    """Recipe object."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField('Tag')
    ingredients = models.ManyToManyField('Ingredient')
    # we pass the function reference in upload_to
    image = models.ImageField(null=True, upload_to=recipe_image_file_path)

    # string representation of this object
    # used in django admin too
    def __str__(self):
        return self.title


class Tag(models.Model):
    """Tag for filtering recipes."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient for recipes."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name
