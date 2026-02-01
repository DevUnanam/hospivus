"""
Views for the user API.
"""
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions
from accounts.api.serializers import (
    UserSerializer,
)
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response


class HealthCheckSerializer(serializers.Serializer):
    healthy = serializers.BooleanField()

@extend_schema(
    tags=["health-check"],
    responses=HealthCheckSerializer,
)
@api_view(["GET"])
def health_check(request):
    """Returns succesful response."""
    return Response({"healthy": True})


@extend_schema(tags=["user"])
class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""

    serializer_class = UserSerializer


@extend_schema(tags=["user"])
class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""

    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user
