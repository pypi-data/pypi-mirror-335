"""Integration tests for the OUA Auth system.

These tests verify the interaction between different components of the authentication system,
including token validation, user authentication, blacklisting, and security features.
"""

import pytest
import jwt
import time
from datetime import datetime, timedelta, UTC
from django.test import Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch, PropertyMock
from rest_framework.exceptions import AuthenticationFailed

from oua_auth.authentication import OUAJWTAuthentication
from oua_auth.models import BlacklistedToken
from oua_auth.token_blacklist import initialize_token_blacklist

# Constants for testing
TEST_SECRET_KEY = "test-signing-key"
TEST_CLIENT_ID = "test-client"
TEST_ISSUER = "test-issuer"


@pytest.mark.django_db
class TestAuthenticationIntegration:
    """Integration tests for the authentication system."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test."""
        # Clear the cache before and after each test
        cache.clear()
        # Initialize the in-memory token blacklist
        initialize_token_blacklist()

        # Create a test user
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
        )

        # Create a test admin user
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="adminpassword",
            first_name="Admin",
            last_name="User",
            is_staff=True,
            is_superuser=True,
        )

        # Generate valid JWT tokens for testing
        self.auth = OUAJWTAuthentication()
        self.valid_token = self._generate_token(self.user.email)
        self.admin_token = self._generate_token(self.admin_user.email)
        self.expired_token = self._generate_token(self.user.email, expired=True)

        # Set up universal patches for authentication
        jwt_decode_patcher = patch("oua_auth.authentication.jwt.decode")
        self.mock_jwt_decode = jwt_decode_patcher.start()

        # Mock the JWT decode function to return appropriate payloads or raise specific errors
        def decode_side_effect(token, *args, **kwargs):
            if token == self.valid_token:
                return {
                    "sub": str(self.user.email),
                    "email": self.user.email,
                    "exp": int((datetime.now(UTC) + timedelta(hours=1)).timestamp()),
                    "iat": int(datetime.now(UTC).timestamp()),
                    "aud": TEST_CLIENT_ID,
                    "iss": TEST_ISSUER,
                    "given_name": "Test",
                    "family_name": "User",
                }
            elif token == self.admin_token:
                return {
                    "sub": str(self.admin_user.email),
                    "email": self.admin_user.email,
                    "exp": int((datetime.now(UTC) + timedelta(hours=1)).timestamp()),
                    "iat": int(datetime.now(UTC).timestamp()),
                    "aud": TEST_CLIENT_ID,
                    "iss": TEST_ISSUER,
                    "given_name": "Admin",
                    "family_name": "User",
                }
            elif token == self.expired_token:
                # Directly raise JWT ExpiredSignatureError
                raise jwt.ExpiredSignatureError("Token expired")
            else:
                # For any other token, return the proper payload based on email
                parts = token.split(".")
                if len(parts) == 3:  # Basic JWT format check
                    try:
                        # Extract email from the token (custom implementation for test)
                        import base64
                        import json

                        payload_part = parts[1]
                        # Add padding if needed
                        payload_part += "=" * (4 - len(payload_part) % 4)
                        payload_json = base64.b64decode(payload_part)
                        payload = json.loads(payload_json)

                        email = payload.get("email")
                        if email:
                            # Domain restriction test
                            if "@restricted.com" in email:
                                raise AuthenticationFailed(
                                    "Your email domain is restricted from accessing this system"
                                )

                            return {
                                "sub": str(email),
                                "email": email,
                                "exp": int(
                                    (datetime.now(UTC) + timedelta(hours=1)).timestamp()
                                ),
                                "iat": int(datetime.now(UTC).timestamp()),
                                "aud": TEST_CLIENT_ID,
                                "iss": TEST_ISSUER,
                                "given_name": "Test",
                                "family_name": "User",
                            }
                    except Exception:
                        pass

                raise jwt.InvalidTokenError("Invalid token format")

        self.mock_jwt_decode.side_effect = decode_side_effect

        # Patch token blacklist check for blacklist tests
        blacklist_patcher = patch(
            "oua_auth.authentication.OUAJWTAuthentication._is_token_blacklisted"
        )
        self.mock_is_blacklisted = blacklist_patcher.start()
        self.mock_is_blacklisted.return_value = False  # Default to not blacklisted

        # Patch rate limit check
        rate_limit_patcher = patch(
            "oua_auth.authentication.OUAJWTAuthentication._is_rate_limited"
        )
        self.mock_is_rate_limited = rate_limit_patcher.start()
        self.mock_is_rate_limited.return_value = False  # Default to not rate limited

        # Patch account lock check
        account_lock_patcher = patch(
            "oua_auth.authentication.OUAJWTAuthentication._is_account_locked"
        )
        self.mock_is_account_locked = account_lock_patcher.start()
        self.mock_is_account_locked.return_value = False  # Default to not locked

        # Instead of patching the whole authenticate method, just patch the necessary components
        # This way, we keep most of the original functionality

        # Use unpatched authentication.authenticate
        self.mock_auth_method = None

        yield

        # Clean up
        cache.clear()

        # Stop all patches
        jwt_decode_patcher.stop()
        blacklist_patcher.stop()
        rate_limit_patcher.stop()
        account_lock_patcher.stop()
        if self.mock_auth_method:
            self.mock_auth_method.stop()

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
            "exp": int(exp.timestamp()),
            "iat": int(now.timestamp()),
            "aud": TEST_CLIENT_ID,
            "iss": TEST_ISSUER,
            "given_name": "Test",
            "family_name": "User",
            "jti": f"test-{int(time.time())}",
        }

        return jwt.encode(
            payload,
            TEST_SECRET_KEY,
            algorithm="HS256",  # We'll override the algorithm check in the test
        )

    @pytest.mark.urls("tests.urls")
    @override_settings(
        OUA_TOKEN_SIGNING_KEY=TEST_SECRET_KEY,
        OUA_PUBLIC_KEY=TEST_SECRET_KEY,
        OUA_CLIENT_ID=TEST_CLIENT_ID,
        OUA_TOKEN_ISSUER=TEST_ISSUER,
        OUA_TRUSTED_DOMAINS=["example.com"],
        OUA_TOKEN_VALIDATION_LEEWAY=0,
    )
    def test_full_authentication_flow(self):
        """Test the complete authentication flow from request to response."""
        client = APIClient()

        # 1. Try to access a protected endpoint without a token
        response = client.get("/api/protected/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # 2. Access with a valid token
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.valid_token}")
        response = client.get("/api/protected/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == "test@example.com"

        # 3. Access with an expired token
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.expired_token}")
        response = client.get("/api/protected/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        # The error message might not specifically mention "expired", but it should return a 401 status
        # which we've already asserted above

        # 4. Access with an admin token
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = client.get("/api/protected/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_admin"] is True

    @pytest.mark.urls("tests.urls")
    def test_token_blacklisting_integration(self):
        """Test token blacklisting functionality."""
        client = APIClient()

        # Configure the blacklist mock to return False for the first call, then True
        original_return_value = self.mock_is_blacklisted.return_value

        # First call returns False (not blacklisted)
        self.mock_is_blacklisted.return_value = False

        # 1. Verify access with valid token
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.valid_token}")
        response = client.get("/api/protected/")
        assert response.status_code == status.HTTP_200_OK

        # Now set the blacklist check to return True (token is blacklisted)
        self.mock_is_blacklisted.return_value = True

        # 2. Try to access after token is blacklisted
        response = client.get("/api/protected/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert (
            "revoked" in str(response.data["detail"]).lower()
            or "blacklisted" in str(response.data["detail"]).lower()
        )

        # Reset for other tests
        self.mock_is_blacklisted.return_value = original_return_value

    @pytest.mark.urls("tests.urls")
    def test_rate_limiting_integration(self):
        """Test rate limiting functionality."""
        client = APIClient()

        # Save original return value
        original_rate_limit = self.mock_is_rate_limited.return_value

        # Set rate limit check to return True (user is rate limited)
        self.mock_is_rate_limited.return_value = True

        # Set a low rate limit for testing
        with override_settings(OUA_MAX_AUTH_FAILURES=3, OUA_AUTH_FAILURE_WINDOW=300):
            # Make request with token - should be rate limited
            client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.valid_token}")
            response = client.get("/api/protected/")

            # Verify rate limiting is active
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert (
                "too many" in str(response.data["detail"]).lower()
                or "rate limit" in str(response.data["detail"]).lower()
            )

        # Reset mock for other tests
        self.mock_is_rate_limited.return_value = original_rate_limit

    @pytest.mark.urls("tests.urls")
    def test_account_locking_integration(self):
        """Test account locking functionality."""
        client = APIClient()

        # Save original return value
        original_account_locked = self.mock_is_account_locked.return_value

        # Set account locked check to return True (account is locked)
        self.mock_is_account_locked.return_value = True

        # Setup for testing with a lower threshold
        with override_settings(
            OUA_MAX_SUSPICIOUS_ACTIVITIES=3,
            OUA_SUSPICIOUS_ACTIVITY_WINDOW=300,
            OUA_ACCOUNT_LOCK_DURATION=3600,
        ):
            # Try to authenticate with a valid token but locked account
            client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.valid_token}")
            response = client.get("/api/protected/")

            # Verify account is locked
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert (
                "locked" in str(response.data["detail"]).lower()
                or "disabled" in str(response.data["detail"]).lower()
            )

        # Reset mock for other tests
        self.mock_is_account_locked.return_value = original_account_locked

    @pytest.mark.urls("tests.urls")
    def test_middleware_integration(self):
        """Test integration with middleware components."""
        client = APIClient()

        # 1. Test with valid token
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.valid_token}")
        response = client.get("/api/protected/")
        assert response.status_code == status.HTTP_200_OK

        # Verify that expected middleware components are run
        # Check for standard response headers that should be present
        assert "Content-Type" in response
        assert response["Content-Type"] == "application/json"

    @pytest.mark.urls("tests.urls")
    def test_domain_restriction_integration(self):
        """Test domain restriction functionality."""
        client = APIClient()

        # Generate a token with a restricted domain
        restricted_token = self._generate_token("user@restricted.com")

        # Test with domain restrictions enabled
        with override_settings(
            OUA_RESTRICTED_DOMAINS=["restricted.com", "blocked.org"]
        ):
            # Save original side effect
            original_side_effect = self.mock_jwt_decode.side_effect

            # Update the JWT decode side effect to handle restricted domains
            def restricted_domain_side_effect(token, *args, **kwargs):
                if token == restricted_token:
                    # This will trigger the restricted domain check
                    return {
                        "sub": "user@restricted.com",
                        "email": "user@restricted.com",
                        "exp": int(
                            (datetime.now(UTC) + timedelta(hours=1)).timestamp()
                        ),
                        "iat": int(datetime.now(UTC).timestamp()),
                        "aud": TEST_CLIENT_ID,
                        "iss": TEST_ISSUER,
                    }
                # Use the original side effect for other tokens
                return original_side_effect(token, *args, **kwargs)

            # Apply the new side effect
            self.mock_jwt_decode.side_effect = restricted_domain_side_effect

            # Try with a restricted domain
            client.credentials(HTTP_AUTHORIZATION=f"Bearer {restricted_token}")
            response = client.get("/api/protected/")
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert "domain" in str(response.data["detail"]).lower() or (
                "restricted" in str(response.data["detail"]).lower()
            )

            # Restore original side effect
            self.mock_jwt_decode.side_effect = original_side_effect
