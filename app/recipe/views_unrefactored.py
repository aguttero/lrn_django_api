# from django.shortcuts import render

"""
Views for the recipe APIs
"""
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication #Auth system we are usign
from rest_framework.permissions import IsAuthenticated # Permission we need to check

from core.models import Recipe, Tag, Ingredient
from recipe import serializers

# ModelViewSet ideal for CRUD ops against Model
class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs.(multiple endpoints)"""
    # serializer_class = serializers.RecipeSerializer
    # most of the methods will use the DetailSerialer
    serializer_class = serializers.RecipeDetailSerializer
    # queryset represents the objects avaialbe for this ModelViewSet
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Override get_queryset to filter recipes of authenticated user
    # Otherwise it gets all recipes
    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    # overrides to custom RecipeSerializer when get_all (list) endpoint is called
    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.RecipeSerializer

        return self.serializer_class

    # Overrides behaviour for when DRF saves a model in a viewset
    # When we create a new objext throuth this viewset using the create feature, we
    # are going to call this method as part of that object creation
    # Call it with the validated serializer as parameter
    # validated data by the viewset before this method us called

    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)

# mixin that allows to add listing func for listing models
# mixins need to be added as parameters before the GenericViewSet
# standard CRUD > GenericViewSet features
class TagViewSet(mixins.DestroyModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Oveerride the std queryset to only return objects for
    # authenticated user
    # otherwise returns all objects (all tags in DB)
    def get_queryset(self):
        """Filter queryset to authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-name')


class IngredientViewSet(mixins.DestroyModelMixin,mixins.UpdateModelMixin,mixins.ListModelMixin, viewsets.GenericViewSet):
    """Manage ingredients in the database."""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-name')
