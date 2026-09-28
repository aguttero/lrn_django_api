"""
Views for the user API.
"""

# from django.shortcuts import render
from rest_framework import generics

from user.serializers import UserSerializer

# Create your views here.

# CreateAPIView handles all logic for POST to create objects in DB
class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""

    serializer_class = UserSerializer
