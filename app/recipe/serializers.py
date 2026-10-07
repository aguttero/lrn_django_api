"""
Serializers for recipe APIs
"""
from rest_framework import serializers

from core.models import Recipe, Tag, Ingredient


# needs to be declared first as will be nested inside
# RecipeSerializer class
class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


# needs to be declared first as will be nested inside
# RecipeSerializer class
class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        # ZAG
        # fields = ['id', 'name', 'user']
        # EZAG
        read_only_fields = ['id']

class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    # this is the codeline to nest a serializer:
    # many > list of tags
    # required = false > optional
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        # list needed fields from table in models.py
        # fields = ['id', 'title', 'time_minutes', 'price', 'link']
        # added 'tags' to nest TagSerializer
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags', 'ingredients']
        read_only_fields = ['id'] # PK

    # internal method from s102 (update tags override write nested field)
    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed."""
        # gets the authenticated user form context
        auth_user = self.context['request'].user

        # loops thru tags we popped out
        # creates tags (or gets if tag already exists)
        # created returns True(created) or False(exists)
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                # could use name=tag['name']
                # **tag allows for new fields in tag in the future (futureproof)
                **tag,
            )
            recipe.tags.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients, recipe):
        """Handle getting or creating ingredients as needed."""
        auth_user = self.context['request'].user
        for ingredient in ingredients:
            ingredient_obj, created = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient,
            )
            recipe.ingredients.add(ingredient_obj)

    # custom logic to override read-only limitation for
    # nested serializer
    def create(self, validated_data):
        """Create a recipe."""
        # pops tags from data
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        # creates recipe object without tags
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)

        return recipe

    # same as create method but adds parameter 'instance'
    # (existing instance to update)
    def update(self, instance, validated_data):
        """Update recipe."""
        # if there is no existing tags we get None
        # if there are, pop generates an empty list []
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        # if tags is an empty list
        if tags is not None:
            # clears all tags in the DB linked to the recipe record
            instance.tags.clear()
            # creates the tags
            self._get_or_create_tags(tags, instance)

        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)

        # loops to assign everything else (except nested values)
        for attr, value in validated_data.items():
            # takes instance and sets the value to the attribute
            setattr(instance, attr, value)

        instance.save()
        return instance


# this is an extension of RecipeSerializer.Meta
class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""

    class Meta(RecipeSerializer.Meta):
        # add detail field from models.py
        fields = RecipeSerializer.Meta.fields + ['description', 'image']


# Separate API / Serializer -> Best Practice to only upload one tipe of
# data to an API.
# when we upload images we only accept the image field
# don't need to accept all the other values that are part of a recipe
class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recipes."""

    class Meta:
        model = Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']
        # image is a required field when uploading an image
        extra_kwargs = {'image': {'required': 'True'}}
