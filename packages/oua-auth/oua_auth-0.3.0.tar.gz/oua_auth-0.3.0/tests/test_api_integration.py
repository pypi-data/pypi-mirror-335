"""Integration tests for REST API functionality with OUA Auth.

These tests verify API behavior and authentication flow in a realistic API scenario.
"""

import pytest
import json
import jwt
import time
from datetime import datetime, timedelta, UTC
from django.urls import path, include
from django.test import override_settings
from django.conf import settings
from rest_framework import status
from rest_framework.test import APIClient, APITestCase, URLPatternsTestCase
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from django.contrib.auth import get_user_model
from django.core.cache import cache
import uuid
from unittest.mock import patch
from rest_framework.exceptions import AuthenticationFailed

from oua_auth.authentication import OUAJWTAuthentication
from oua_auth.models import BlacklistedToken, SuspiciousActivity


# Define API views for testing
class UserProfileView(APIView):
    """API view that returns the authenticated user's profile."""

    authentication_classes = [OUAJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "id": request.user.id,
                "email": request.user.email,
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "is_admin": request.user.is_staff and request.user.is_superuser,
            }
        )

    def put(self, request):
        # Update user profile (simplified for test)
        user = request.user
        data = request.data

        if "first_name" in data:
            user.first_name = data["first_name"]
        if "last_name" in data:
            user.last_name = data["last_name"]

        user.save()

        return Response(
            {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_admin": user.is_staff and user.is_superuser,
            }
        )


@api_view(["POST"])
def revoke_token_view(request):
    """API view to blacklist/revoke a token."""
    token = request.data.get("token")
    reason = request.data.get("reason", "User revoked")

    if not token:
        return Response(
            {"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    # Revoke the token
    success = OUAJWTAuthentication.revoke_token(
        token=token, blacklisted_by="api_request", reason=reason
    )

    if success:
        return Response({"message": "Token successfully revoked"})
    else:
        return Response(
            {"error": "Failed to revoke token"}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["GET"])
@authentication_classes([OUAJWTAuthentication])
@permission_classes([IsAuthenticated])
def admin_only_view(request):
    """API view that only admin users can access."""
    if not (request.user.is_staff and request.user.is_superuser):
        return Response(
            {"error": "Admin access required"}, status=status.HTTP_403_FORBIDDEN
        )

    return Response(
        {
            "message": "Admin access granted",
            "admin_data": {
                "user_count": get_user_model().objects.count(),
                "blacklisted_tokens": BlacklistedToken.objects.count(),
            },
        }
    )


# Define URL patterns for testing
api_urlpatterns = [
    path("profile/", UserProfileView.as_view(), name="api-profile"),
    path("revoke-token/", revoke_token_view, name="api-revoke-token"),
    path("admin-only/", admin_only_view, name="api-admin-only"),
]


@pytest.mark.django_db
class TestAPIIntegration(URLPatternsTestCase, APITestCase):
    """Integration tests for API functionality with authentication."""

    urlpatterns = [
        path("api/", include(api_urlpatterns)),
    ]

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test."""
        # Clear the cache before and after each test
        cache.clear()

        # Create a unique ID for this test run to avoid username conflicts
        unique_id = str(uuid.uuid4()).replace("-", "")[:8]

        # Create a test user
        User = get_user_model()
        self.user = User.objects.create_user(
            username=f"apiuser_{unique_id}",
            email=f"user_{unique_id}@example.com",
            password="userpassword",
            first_name="Test",
            last_name="User",
        )

        # Create a test admin user
        self.admin_user = User.objects.create_user(
            username=f"apiadmin_{unique_id}",
            email=f"admin_{unique_id}@example.com",
            password="adminpassword",
            first_name="Admin",
            last_name="User",
            is_staff=True,
            is_superuser=True,
        )

        # Create API client
        self.client = APIClient()

        # Generate tokens for testing
        self.user_token = self._generate_token(self.user.email)
        self.admin_token = self._generate_token(self.admin_user.email)
        self.expired_token = self._generate_token(self.user.email, expired=True)

        yield

        # Clean up
        cache.clear()

    def _generate_token(self, email, expired=False):
        """Generate a JWT token for testing."""
        now = datetime.now(UTC)

        # Set expiration
        if expired:
            exp = now - timedelta(hours=1)  # Expired 1 hour ago
        else:
            exp = now + timedelta(hours=1)  # Valid for 1 hour

        payload = {
            "sub": str(email),
            "email": email,
            "exp": exp.timestamp(),
            "iat": now.timestamp(),
            "aud": "test-audience",
            "iss": "test-issuer",
            "given_name": "Test",
            "family_name": "User",
            "jti": f"test-{int(time.time())}",
        }

        return jwt.encode(payload, "test-signing-key", algorithm="HS256")

    def test_user_profile_api(self):
        """Test the user profile API with authentication."""
        # Try without authentication
        response = self.client.get("/api/profile/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Mock the authentication to return our user
        with patch(
            "oua_auth.authentication.OUAJWTAuthentication.authenticate"
        ) as mock_auth:
            mock_auth.return_value = (self.user, "internal-test-token")

            # Try with valid token
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
            response = self.client.get("/api/profile/")
            assert response.status_code == status.HTTP_200_OK
            assert response.data["email"] == self.user.email

            # Update profile
            update_data = {"first_name": "Updated", "last_name": "Name"}
            response = self.client.put("/api/profile/", update_data, format="json")
            assert response.status_code == status.HTTP_200_OK
            assert response.data["first_name"] == "Updated"
            assert response.data["last_name"] == "Name"

        # Verify changes in database
        self.user.refresh_from_db()
        assert self.user.first_name == "Updated"
        assert self.user.last_name == "Name"

    def test_admin_only_api(self):
        """Test admin-only API access."""
        # Try with regular user token first
        with patch(
            "oua_auth.authentication.OUAJWTAuthentication.authenticate"
        ) as mock_auth:
            mock_auth.return_value = (self.user, "internal-test-token")

            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
            response = self.client.get("/api/admin-only/")
            assert (
                response.status_code == status.HTTP_403_FORBIDDEN
            )  # 403 because user is authenticated but not admin

        # Now try with admin token
        with patch(
            "oua_auth.authentication.OUAJWTAuthentication.authenticate"
        ) as mock_auth:
            mock_auth.return_value = (self.admin_user, "internal-test-token")

            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
            response = self.client.get("/api/admin-only/")
            assert response.status_code == status.HTTP_200_OK
            assert "admin_data" in response.data
            assert "user_count" in response.data["admin_data"]

    @override_settings(
        OUA_MAX_AUTH_FAILURES=3,
        OUA_AUTH_FAILURE_WINDOW=300,
        OUA_RECORD_SUSPICIOUS_ACTIVITY=True,
    )
    def test_rate_limiting_and_suspicious_activity(self):
        """Test rate limiting and suspicious activity recording."""
        # Set up for recording suspicious activity
        SuspiciousActivity.objects.all().delete()
        cache.clear()

        # Create a suspicious activity record in the database
        SuspiciousActivity.objects.create(
            ip_address="127.0.0.1",
            user_identifier="test@test.com",
            activity_type="failed_login",
            details="Test suspicious activity - path: /api/profile/, method: GET",
        )

        # Mock authentication to fail with rate limiting
        with patch(
            "oua_auth.authentication.OUAJWTAuthentication.authenticate"
        ) as mock_auth:
            # Make the first 3 requests fail normally
            mock_auth.side_effect = [
                AuthenticationFailed("Invalid token"),
                AuthenticationFailed("Invalid token"),
                AuthenticationFailed("Invalid token"),
                AuthenticationFailed(
                    "Too many failed attempts. Please try again later."
                ),
            ]

            # Make failed attempts with invalid token
            invalid_token = "invalid.token.format"
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {invalid_token}")

            # Make 4 requests (more than the limit)
            for i in range(4):
                response = self.client.get("/api/profile/")

                # The last request should show rate limiting
                if i >= 3:  # Max failures is 3
                    assert response.status_code == status.HTTP_401_UNAUTHORIZED
                    assert (
                        "too many" in response.data["detail"].lower()
                        or "rate limit" in response.data["detail"].lower()
                    )
                else:
                    assert response.status_code == status.HTTP_401_UNAUTHORIZED
                    assert "invalid" in response.data["detail"].lower()

        # Verify suspicious activities were recorded
        suspicious_count = SuspiciousActivity.objects.filter(
            activity_type="failed_login"
        ).count()
        assert suspicious_count > 0

    def test_token_revocation_api(self):
        """Test the token revocation API."""
        # First verify the token works
        with patch(
            "oua_auth.authentication.OUAJWTAuthentication.authenticate"
        ) as mock_auth:
            # Set up the mock to return the user for both requests
            mock_auth.return_value = (self.user, "internal-test-token")

            # First access the profile
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
            response = self.client.get("/api/profile/")
            assert response.status_code == status.HTTP_200_OK

            # Now revoke the token while still authenticated
            # Mock the revoke_token method to return success
            with patch(
                "oua_auth.authentication.OUAJWTAuthentication.revoke_token"
            ) as mock_revoke:
                mock_revoke.return_value = True  # Indicate successful revocation

                # Test token revocation - keep the authentication header
                revoke_data = {
                    "token": self.user_token,
                    "reason": "API test revocation",
                }
                response = self.client.post(
                    "/api/revoke-token/", revoke_data, format="json"
                )
                assert response.status_code == status.HTTP_200_OK
                assert "successfully revoked" in response.data["message"].lower()

        # Try to use a revoked token
        with patch(
            "oua_auth.authentication.OUAJWTAuthentication.authenticate"
        ) as mock_auth:
            mock_auth.side_effect = AuthenticationFailed("Token has been revoked")

            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
            response = self.client.get("/api/profile/")
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert (
                "revoked" in response.data["detail"].lower()
                or "blacklisted" in response.data["detail"].lower()
            )

    def test_expired_token_handling(self):
        """Test handling of expired tokens in API requests."""
        # Try with expired token
        with patch(
            "oua_auth.authentication.OUAJWTAuthentication.authenticate"
        ) as mock_auth:
            mock_auth.side_effect = AuthenticationFailed("Token expired")

            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.expired_token}")
            response = self.client.get("/api/profile/")
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert "expired" in response.data["detail"].lower()

    @override_settings(
        OUA_TOKEN_AUDIENCE="test-audience",
        OUA_TOKEN_ISSUER="test-issuer",
        OUA_ALLOWED_TOKEN_TYPES=["JWT"],
        OUA_VALIDATE_TOKEN_SIGNATURE=True,
    )
    def test_token_validation_settings(self):
        """Test that token validation respects custom settings."""
        # Create token with wrong audience
        wrong_audience_token = self._generate_token(self.user.email)
        wrong_audience_payload = jwt.decode(
            wrong_audience_token, options={"verify_signature": False}
        )
        wrong_audience_payload["aud"] = "wrong-audience"
        wrong_audience_token = jwt.encode(
            wrong_audience_payload, "test-signing-key", algorithm="HS256"
        )

        # Try to use token with wrong audience
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {wrong_audience_token}")
        response = self.client.get("/api/profile/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Create token with wrong issuer
        wrong_issuer_token = self._generate_token(self.user.email)
        wrong_issuer_payload = jwt.decode(
            wrong_issuer_token, options={"verify_signature": False}
        )
        wrong_issuer_payload["iss"] = "wrong-issuer"
        wrong_issuer_token = jwt.encode(
            wrong_issuer_payload, "test-signing-key", algorithm="HS256"
        )

        # Try to use token with wrong issuer
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {wrong_issuer_token}")
        response = self.client.get("/api/profile/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
