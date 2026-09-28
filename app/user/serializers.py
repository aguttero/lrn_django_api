"""
Serializers for the user API View.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers


# Create class UserSerializer from Django ModelSerializer
class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    # defines what the serializer is going to be used for:
    # what model > get_user_model
    # which fields (email, pwd, name) only fields that
    # a user will provide when requesting to create a user
    # extra_kwargs, additional metadata to different fields
    class Meta:
        model = get_user_model()
        fields = ["email", "password", "name"]
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    # this method allows to override the default create method
    # from the serializer so that we can use the one that is in
    # the return codeline
    # this method is only called if validation from Meta passes ok
    def create(self, validated_data):
        """Create and return a user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)
