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

    # custom logic to override read-only limitation for
    # nested serializer
    def create(self, validated_data):
        """Create a recipe."""
        # pops tags from data
        tags = validated_data.pop('tags', [])
        # creates recipe object without tags
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)

        return recipe

    # same as create method but adds parameter 'instance'
    # (existing instance to update)
    def update(self, instance, validated_data):
        """Update recipe."""
        # if there is no existing tags we get None
        # if there are, pop generates an empty list []
        tags = validated_data.pop('tags', None)
        # if tags is an empty list
        if tags is not None:
            # clears all tags in the DB linked to the recipe record
            instance.tags.clear()
            # creates the tags
            self._get_or_create_tags(tags, instance)

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
        fields = RecipeSerializer.Meta.fields + ['description']
