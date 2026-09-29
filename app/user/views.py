"""
Views for the user API.
"""

# from django.shortcuts import render
from rest_framework import authentication, generics, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import AuthTokenSerializer, UserSerializer


# CreateAPIView handles all logic for POST to create objects in DB
class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""

    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""

    # this to customize serializer because we use email instead of
    # username which is the default in django
    serializer_class = AuthTokenSerializer
    # uses the default rendered clases for this obtaintauthtokeview
    # to make sure that the browsable api shows the user interface
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""

    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    # The permission level needed to use this endpoint is that
    # the user is authenticated.
    permission_classes = [permissions.IsAuthenticated]

    # Override the get_object method and only retreive the user
    # that is attached to the request
    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user
