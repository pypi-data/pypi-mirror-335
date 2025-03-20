"""URL configuration for testing.

This module contains URL patterns used exclusively for testing purposes.
"""

from django.urls import path
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from oua_auth.authentication import OUAJWTAuthentication


@api_view(["GET", "POST"])
@authentication_classes([OUAJWTAuthentication])
@permission_classes([IsAuthenticated])
def protected_view(request):
    """A protected view that requires authentication."""
    # Return user information from the authenticated request
    return Response(
        {
            "email": request.user.email,
            "username": getattr(request.user, "username", None),
            "is_admin": request.user.is_staff and request.user.is_superuser,
            "internal_token": getattr(request, "internal_token", None),
            "message": "You have successfully accessed the protected endpoint!",
        }
    )


urlpatterns = [
    path("api/protected/", protected_view, name="protected"),
]
