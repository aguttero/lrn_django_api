"""
Serializers for the user API View.
"""

from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext as _
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

    def update(self, instance, validated_data):
        """Update and return user."""
        # pop password. retrieve from validated data model and remove it.
        # .get would retrieve it and leave it
        # the user may want to update name or email address (not pwd)
        # If user didn't provide a password we default to None
        password = validated_data.pop('password', None)
        # we call super().update to leverage existing update method
        user = super().update(instance, validated_data)

        # check if password was specified in the update call and saves it
        if password:
            user.set_password(password)
            user.save()

        # ZAG
        print (user)
        # EZAG
        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""

    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"},
        trim_whitespace=False,
    )
    # this style makes the browser hide the pwd text
    # don't trim the space at the end if the user added it on purpose

    def validate(self, attrs):
        """Validate and authenticate the user."""
        email = attrs.get("email")
        password = attrs.get("password")
        # authenticate is a django OOB function
        # checks if the user is ok
        # if it is ok returns user, else returns None
        # request= request is a requirement from django

        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password,
        )
        if not user:
            msg = _("Unable to authenticate with provided credentials.")
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs
