"""
Revoke-token endpoints. Split each block into the file named in its header.
"""

# =====================================================================
# user/serializers.py  (add this class)
# =====================================================================
from rest_framework import serializers


class RevokeUserTokenSerializer(serializers.Serializer):
    """Input for the admin endpoint: the email of the user to log out."""

    email = serializers.EmailField()


# =====================================================================
# user/views.py  (replace your RevokeTokenView and add the admin one)
# =====================================================================
from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import authentication, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from user.serializers import RevokeUserTokenSerializer


@extend_schema(
    request=None,
    responses={200: OpenApiResponse(description="Successfully logged out.")},
)
class RevokeTokenView(APIView):
    """Logout: the authenticated user revokes their own token."""

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # request.auth is the Token instance used to authenticate this call
        request.auth.delete()
        return Response(
            {"detail": "Successfully logged out."}, status=status.HTTP_200_OK
        )


@extend_schema(
    request=RevokeUserTokenSerializer,
    responses={
        200: OpenApiResponse(description="Token revoked."),
        404: OpenApiResponse(description="User not found."),
    },
)
class AdminRevokeUserTokenView(APIView):
    """Admin (is_staff) revokes the token of any user, identified by email."""

    authentication_classes = [authentication.TokenAuthentication]
    # IsAdminUser checks user.is_staff. For superusers only, use a custom
    # permission class that checks user.is_superuser instead.
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        serializer = RevokeUserTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        # iexact: normalize_email only lowercases the domain part
        try:
            user = get_user_model().objects.get(email__iexact=email)
        except get_user_model().DoesNotExist:
            return Response(
                {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # DRF Token is one-to-one with user, so this deletes at most one row
        deleted, _ = Token.objects.filter(user=user).delete()

        detail = (
            f"Token for {user.email} revoked."
            if deleted
            else f"{user.email} had no active token."
        )
        return Response({"detail": detail}, status=status.HTTP_200_OK)


# =====================================================================
# user/urls.py  (add the routes)
# =====================================================================
# from django.urls import path
# from user import views
#
# urlpatterns = [
#     ...
#     path("logout/", views.RevokeTokenView.as_view(), name="logout"),
#     path("revoke/", views.AdminRevokeUserTokenView.as_view(), name="revoke"),
# ]
#
# Usage:
#   POST /api/user/logout/   (Authorization: Token <own token>)
#   POST /api/user/revoke/   (Authorization: Token <admin token>)
#        body: {"email": "someone@example.com"}
