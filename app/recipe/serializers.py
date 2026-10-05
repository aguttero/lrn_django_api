"""
Serializers for recipe APIs
"""
from rest_framework import serializers

from core.models import Recipe, Tag

# needs to be declared first as will be nested inside
# RecipeSerializer class
class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']

class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    # this is the codeline to nest a serializer:
    # many > list of tags
    # required = false > optional
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        # list needed fields from table in models.py
        # fields = ['id', 'title', 'time_minutes', 'price', 'link']
        # added 'tags' to nest TagSerializer
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags']
        read_only_fields = ['id'] # PK

    # custom logic to override read-only limitation for
    # nested serializer
    def create(self, validated_data):
        """Create a recipe."""
        # pops tags from data
        tags = validated_data.pop('tags', [])
        # crates recipe object without tags
        recipe = Recipe.objects.create(**validated_data)
        # gets the authenticated user form context
        auth_user = self.context['request'].user

        # creates tags (or gtets if tag already exists)
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipe.tags.add(tag_obj)

        return recipe


# this is an extension of RecipeSerializer.Meta
class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""

    class Meta(RecipeSerializer.Meta):
        # add detail field from models.py
        fields = RecipeSerializer.Meta.fields + ['description']
