"""
Tests for recipe APIs.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag

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

def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


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
        # ZAG s87 refactor to helpèr function
        # self.user = get_user_model().objects.create_user(
        #     'user@example.com',
        #     'testpass123',
        # )
        self.user = create_user(email='user@example.com', password='test123')
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
        # print ("data comparison:")
        # print ("api response:")
        # print (res.data)
        # print ("db serialized data:")
        # print (serializer.data)
        # print ("- - - ")
        # EZAG

    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user."""
        # ZAG s87 refactor to helper function
        # other_user = get_user_model().objects.create_user(
        #     'other@example.com',
        #     'password123',
        # )
        other_user = create_user(email='other@example.com', password='test123')
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


    def test_create_recipe(self):
        """Test creating a recipe.(actual api call test)"""
        payload = {
            'title': 'Sample recipe',
            'time_minutes': 30,
            'price': Decimal('5.99'),
        }
        # POST to apiendpoint create recipe
        res = self.client.post(RECIPES_URL, payload)

        # Validates OK 201 CREATED Response
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # retrieve from DB recipe just created which ID was received from api response payload
        recipe = Recipe.objects.get(id=res.data['id'])

        # Key, Value in Dict
        # Compares recipe (DB) vs payload dict
        for k, v in payload.items():
            # different to recipe.k
            self.assertEqual(getattr(recipe, k), v)
            # ZAG
            print ("kv comparison")
            print("k:", k)
            # recipe.k generates error no attribute.k
            # print ("recipe.k:",recipe.k)
            print ("getattr:", getattr(recipe, k))
            print ("- - - ")
            # E ZAG
        # Compares user assigned to api matches the user we are authenticated with
        self.assertEqual(recipe.user, self.user)

    # S87 additional tests
    def test_partial_update(self):
        """Test partial update of a recipe."""
        original_link = 'https://example.com/recipe.pdf'
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe title',
            link=original_link,
        )

        # Updated / Patched title field
        payload = {'title': 'New recipe title'}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test full update of recipe."""
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe title',
            link='https://exmaple.com/recipe.pdf',
            description='Sample recipe description.',
        )

        # PUT> full update to recipe
        payload = {
            'title': 'New recipe title',
            'link': 'https://example.com/new-recipe.pdf',
            'description': 'New recipe description',
            'time_minutes': 10,
            'price': Decimal('2.50'),
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        # loop compares recipe in DB vs PUT payload
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    # Test to update the user assigned to a recipe returns error
    # The API design does not allow to change the recipe author (user)
    def test_update_user_returns_error(self):
        """Test changing the recipe user results in an error."""
        new_user = create_user(email='user2@example.com', password='test123')
        recipe = create_recipe(user=self.user)

        # PATCH recipe.user with new user
        payload = {'user': new_user.id}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    # Standard delete opereation
    def test_delete_recipe(self):
        """Test deleting a recipe successful."""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    # TEST try to delete a recipe from another user
    def test_recipe_other_users_recipe_error(self):
        """Test trying to delete another users recipe gives error."""
        new_user = create_user(email='user2@example.com', password='test123')
        recipe = create_recipe(user=new_user)

        url = detail_url(recipe.id)
        # self calls with self.user not with new_user
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    # s99 Nested Serializers
    def test_create_recipe_with_new_tags(self):
        """Test creating a recipe with new tags."""
        payload = {
            'title': 'Thai Prawn Curry',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'tags': [{'name': 'Thai'}, {'name': 'Dinner'}],
        }
        # format='json' because there are nested objects in the payload
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        # validate that there is only 1 recipe
        self.assertEqual(recipes.count(), 1)
        # recipe takes the value of the first element
        recipe = recipes[0]
        # ZAG
        print("recipes_query:", recipes)
        print("recipe[0]:", recipe)
        print("- - - ")
        # EZAG
        # validate 2 tags
        self.assertEqual(recipe.tags.count(), 2)
        # loop 2 tags and check that they exist and compares to query
        # exists busca en la DB las tags de recipe por nombre y
        # usuario coincida. Si las encuentra devuelve True y si no false
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    # to avoid duplicate tags in DB
    def test_create_recipe_with_existing_tags(self):
        """Test creating a recipe with existing tag."""
        tag_indian = Tag.objects.create(user=self.user, name='Indian')
        payload = {
            'title': 'Pongal',
            'time_minutes': 60,
            'price': Decimal('4.50'),
            'tags': [{'name': 'Indian'}, {'name': 'Breakfast'}],
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        # validates that the tag was not duplicated
        self.assertIn(tag_indian, recipe.tags.all())
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)
