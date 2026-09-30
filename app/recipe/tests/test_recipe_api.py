"""
Tests for recipe APIs.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse('recipe:recipe-list')

# This is a function instead of a fixed URL because the URL contains the recipe id
def detail_url(recipe_id):
    """Create and return a recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])

# params will be a dictionary of parameters passed
# defaults are there and can be overriden by what we pass
# override -> defaults.update(params)
# user is a required parameter
def create_recipe(user, **params):
    """Create and return a sample recipe."""
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample description',
        'link': 'http://example.com/recipe.pdf',
    }
    # best practice: update default dict with data in params, to
    # avoid transforming a received dictionary
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    # returno recipe object instance that was created
    return recipe


class PublicRecipeAPITests(TestCase):
    """Test unauthenticated API requests."""

    # unittest module defines that setUp() is with camelcase
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes."""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        # api cal to recipes
        res = self.client.get(RECIPES_URL)
        # ZAG
        print ("api response:")
        print (res)
        print ("- - - ")
        # EZAG

        # recipes in DB
        recipes = Recipe.objects.all().order_by('-id')
        # serialized recipes
        # many=True -> serializers can either return a detail o can return
        # a list of items. many=True -> list of items
        serializer = RecipeSerializer(recipes, many=True)

        # validates 200 OK response
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # compares api responsdata against DB data
        self.assertEqual(res.data, serializer.data)
        # ZAG
        print ("data comparison:")
        print ("api response:")
        print (res.data)
        print ("db serialized data:")
        print (serializer.data)
        print ("- - - ")
        # EZAG

    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user."""
        other_user = get_user_model().objects.create_user(
            'other@example.com',
            'password123',
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test get recipe detail."""
        # create a recipe
        recipe = create_recipe(user=self.user)

        # define the URL
        url = detail_url(recipe.id)

        # call endpoint
        res = self.client.get(url)

        # serialize the recipe from DB
        serializer = RecipeDetailSerializer(recipe)

        # compare api response vs serialized DB recipe
        self.assertEqual(res.data, serializer.data)
