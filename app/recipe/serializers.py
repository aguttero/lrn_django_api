"""
Serializers for recipe APIs
"""
from rest_framework import serializers

from core.models import Recipe, Tag


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""

    class Meta:
        model = Recipe
        # list needed fields from table in models.py
        fields = ['id', 'title', 'time_minutes', 'price', 'link']
        read_only_fields = ['id'] # PK


# this is an extension of RecipeSerializer.Meta
class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""

    class Meta(RecipeSerializer.Meta):
        # add detail field from models.py
        fields = RecipeSerializer.Meta.fields + ['description']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']
