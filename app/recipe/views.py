# from django.shortcuts import render

"""
Views for the recipe APIs
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication #Auth system we are usign
from rest_framework.permissions import IsAuthenticated # Permission we need to check

from core.models import Recipe
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
