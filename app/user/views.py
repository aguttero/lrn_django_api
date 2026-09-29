"""
Views for the user API.
"""

# from django.shortcuts import render
from rest_framework import authentication, generics, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

# for the logout:
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

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


@extend_schema(
    request=None,  # Tells Swagger that no request body / serializer is required
    responses={200: dict(detail="Successfully logged out. YEAH")}, # Optional: documents the response
)

class RevokeTokenView(APIView):
    """Logout the user by revoking/deleting their auth token."""

    # serializer_class = UserSerializer
    # serializer_class = AuthTokenSerializer
    # renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    # def get_object(self):
    #     """Retrieve and return the authenticated user."""
    #     return self.request.user

    def post(self, request):
        """Delete the token associated with the current authorized user."""
        # request.auth contains the Token database object for the current session
        request.auth.delete()
        return Response(
            # {"detail": "Successfully logged out."}, status=200
            {"detail": "Successfully logged out."}, status=status.HTTP_200_OK
        )
