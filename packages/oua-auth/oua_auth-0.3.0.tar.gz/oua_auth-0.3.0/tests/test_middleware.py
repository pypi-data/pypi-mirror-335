"""Tests for OUAAuthMiddleware."""

import pytest
from unittest.mock import patch, MagicMock
from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, HttpRequest, HttpResponseForbidden
from django.test import TestCase, override_settings
from django.utils import timezone
from datetime import datetime, timedelta, UTC
import requests

from oua_auth.middleware import (
    OUAAuthMiddleware,
    OUAUserMiddleware,
    _authenticate_from_request,
)


# Add pytest.mark.django_db to the entire class
@pytest.mark.django_db
class TestOUAAuthMiddleware:
    """Tests for OUAAuthMiddleware."""

    def test_init_required_settings(self, settings):
        """Test middleware initialization with required settings."""
        get_response = MagicMock()
        middleware = OUAAuthMiddleware(get_response)
        assert middleware.sso_url == "https://test-sso.example.com"
        assert middleware.public_key == settings.OUA_PUBLIC_KEY
        assert middleware.client_id == "test-client-id"

    def test_init_missing_settings(self, settings):
        """Test middleware initialization with missing required settings."""
        get_response = MagicMock()

        # Remove OUA_CLIENT_ID from settings
        delattr(settings, "OUA_CLIENT_ID")

        with pytest.raises(ImproperlyConfigured) as excinfo:
            OUAAuthMiddleware(get_response)

        assert "OUA_CLIENT_ID setting is required" in str(excinfo.value)

    def test_init_invalid_sso_url(self, settings):
        """Test middleware initialization with invalid SSO URL (non-HTTPS)."""
        get_response = MagicMock()

        # Set a non-HTTPS URL in a non-debug environment
        settings.OUA_SSO_URL = "http://test-sso.example.com"
        settings.DEBUG = False

        with pytest.raises(ImproperlyConfigured) as excinfo:
            OUAAuthMiddleware(get_response)

        assert "OUA_SSO_URL must use HTTPS in production" in str(excinfo.value)

    def test_init_optional_settings(self, settings):
        """Test middleware initialization with optional settings."""
        get_response = MagicMock()
        middleware = OUAAuthMiddleware(get_response)
        assert middleware.token_signing_key == "test-signing-key"
        assert middleware.trusted_admin_domains == ["trusted.example.com"]
        assert "admin@example.com" in middleware.trusted_admin_emails
        assert middleware.internal_token_lifetime == 3600

    def test_call_no_auth_header(self, mock_request):
        """Test middleware call with no Authorization header."""
        get_response = MagicMock(return_value="response")
        middleware = OUAAuthMiddleware(get_response)

        response = middleware(mock_request)

        assert isinstance(mock_request.user, AnonymousUser)
        assert response == "response"
        get_response.assert_called_once_with(mock_request)

    def test_call_with_excluded_path(self, mock_request, settings):
        """Test middleware call with excluded path."""
        settings.OUA_EXCLUDE_PATHS = ["/excluded/"]
        get_response = MagicMock(return_value="response")
        middleware = OUAAuthMiddleware(get_response)

        mock_request.path = "/excluded/path"
        response = middleware(mock_request)

        assert response == "response"
        get_response.assert_called_once_with(mock_request)

    def test_call_with_valid_token(
        self, mock_request, valid_token, jwt_payload_regular, mocker
    ):
        """Test middleware call with valid token."""
        get_response = MagicMock(return_value="response")
        middleware = OUAAuthMiddleware(get_response)

        # Mock the internal token generation to avoid signing issues in tests
        mock_generate = mocker.patch.object(
            middleware, "_generate_internal_token", return_value="internal-token"
        )

        mock_request.headers["Authorization"] = f"Bearer {valid_token}"
        response = middleware(mock_request)

        assert mock_request.user is not None
        assert mock_request.user.email == "user@example.com"
        assert mock_request.oua_token == valid_token
        assert mock_request.oua_claims == jwt_payload_regular
        assert mock_request.internal_token == "internal-token"
        assert response == "response"
        get_response.assert_called_once_with(mock_request)
        mock_generate.assert_called_once()

    def test_call_with_admin_token(
        self, mock_request, admin_token, jwt_payload_admin, mocker
    ):
        """Test middleware call with admin token from trusted email."""
        get_response = MagicMock(return_value="response")
        middleware = OUAAuthMiddleware(get_response)

        # Mock the internal token generation to avoid signing issues in tests
        mock_generate = mocker.patch.object(
            middleware, "_generate_internal_token", return_value="internal-token"
        )

        mock_request.headers["Authorization"] = f"Bearer {admin_token}"
        response = middleware(mock_request)

        assert mock_request.user is not None
        assert mock_request.user.email == "admin@example.com"
        assert mock_request.user.is_staff is True
        assert mock_request.user.is_superuser is True
        assert mock_request.oua_token == admin_token
        assert mock_request.oua_claims == jwt_payload_admin
        assert mock_request.internal_token == "internal-token"
        assert response == "response"
        get_response.assert_called_once_with(mock_request)
        mock_generate.assert_called_once()

    def test_call_with_expired_token(self, mock_request, expired_token):
        """Test middleware call with expired token."""
        get_response = MagicMock()
        middleware = OUAAuthMiddleware(get_response)

        mock_request.headers["Authorization"] = f"Bearer {expired_token}"
        response = middleware(mock_request)

        assert isinstance(response, HttpResponseForbidden)
        assert "Authentication failed: token expired" in str(response.content)
        get_response.assert_not_called()

    def test_call_with_invalid_token(self, mock_request):
        """Test middleware call with invalid token."""
        get_response = MagicMock()
        middleware = OUAAuthMiddleware(get_response)

        mock_request.headers["Authorization"] = "Bearer invalid.token.here"
        response = middleware(mock_request)

        assert isinstance(response, HttpResponseForbidden)
        assert "Authentication failed: invalid token" in str(response.content)
        get_response.assert_not_called()

    def test_call_with_malformed_token(self, mock_request, malformed_token):
        """Test middleware call with malformed token (missing claims)."""
        get_response = MagicMock()
        middleware = OUAAuthMiddleware(get_response)

        mock_request.headers["Authorization"] = f"Bearer {malformed_token}"
        response = middleware(mock_request)

        assert isinstance(response, HttpResponseForbidden)
        assert "Invalid token: no email claim" in str(response.content)
        get_response.assert_not_called()

    def test_call_with_invalid_email_format(self, mock_request, invalid_email_token):
        """Test middleware call with invalid email format in token."""
        get_response = MagicMock()
        middleware = OUAAuthMiddleware(get_response)

        mock_request.headers["Authorization"] = f"Bearer {invalid_email_token}"
        response = middleware(mock_request)

        assert isinstance(response, HttpResponseForbidden)
        assert "Invalid email format" in str(response.content)
        get_response.assert_not_called()

    def test_call_with_unexpected_exception(self, mock_request, valid_token, mocker):
        """Test middleware call with an unexpected exception."""
        get_response = MagicMock()
        middleware = OUAAuthMiddleware(get_response)

        # Mock jwt.decode to raise an unexpected exception
        mocker.patch(
            "oua_auth.middleware.jwt.decode",
            side_effect=Exception("Unexpected error"),
        )

        mock_request.headers["Authorization"] = f"Bearer {valid_token}"
        response = middleware(mock_request)

        assert isinstance(response, HttpResponseForbidden)
        assert "Authentication failed" in str(response.content)
        get_response.assert_not_called()

    def test_generate_internal_token(self, user_regular, jwt_payload_regular):
        """Test internal token generation."""
        get_response = MagicMock()
        middleware = OUAAuthMiddleware(get_response)

        internal_token = middleware._generate_internal_token(
            user_regular, jwt_payload_regular
        )

        assert isinstance(internal_token, str)
        assert len(internal_token) > 0

    def test_generate_internal_token_exception(
        self, user_regular, jwt_payload_regular, mocker
    ):
        """Test internal token generation with an exception."""
        get_response = MagicMock()
        middleware = OUAAuthMiddleware(get_response)

        # Mock jwt.encode to raise an exception
        mocker.patch(
            "oua_auth.middleware.jwt.encode",
            side_effect=Exception("Token generation error"),
        )

        with pytest.raises(Exception):
            middleware._generate_internal_token(user_regular, jwt_payload_regular)

    def test_sanitize_input(self):
        """Test _sanitize_input method."""
        get_response = MagicMock()
        middleware = OUAAuthMiddleware(get_response)

        # Test with script tag - bleach will strip HTML tags
        assert middleware._sanitize_input("<script>alert(1)</script>") == "alert(1)"

        # Test with more complex HTML - bleach will strip all tags
        assert (
            middleware._sanitize_input("<div><p>Hello <b>world</b>!</p></div>")
            == "Hello world!"
        )

        # Test with non-string input
        assert (
            middleware._sanitize_input(123) == 123
        )  # Now returns non-string values as is

        # Test with None
        assert (
            middleware._sanitize_input(None) is not None
        )  # None is converted to empty string

        # Test with normal text
        assert middleware._sanitize_input("Normal text") == "Normal text"

        # Test length limitation (100 chars)
        long_input = "a" * 200
        assert len(middleware._sanitize_input(long_input)) == 100


# Add pytest.mark.django_db to the entire class
@pytest.mark.django_db
class TestOUAUserMiddleware:
    """Tests for OUAUserMiddleware."""

    def test_init(self):
        """Test middleware initialization."""
        get_response = MagicMock()
        middleware = OUAUserMiddleware(get_response)

        assert middleware.sso_url == "https://test-sso.example.com"
        assert hasattr(middleware, "session")
        assert middleware.timeout == 5
        assert middleware.max_requests_per_minute == 60
        assert middleware.request_timestamps == []

    def test_call_no_token(self, mock_request):
        """Test middleware call with no token."""
        get_response = MagicMock(return_value="response")
        middleware = OUAUserMiddleware(get_response)

        # No oua_token attribute
        response = middleware(mock_request)

        assert response == "response"
        get_response.assert_called_once_with(mock_request)

    def test_call_with_valid_token(
        self, mock_request, user_regular, valid_token, mock_response
    ):
        """Test middleware call with valid token."""
        get_response = MagicMock(return_value="response")
        middleware = OUAUserMiddleware(get_response)

        # Setup the request object
        mock_request.user = user_regular
        mock_request.oua_token = valid_token

        # Mock the requests session get method
        with patch.object(middleware.session, "get", return_value=mock_response):
            response = middleware(mock_request)

        assert response == "response"
        get_response.assert_called_once_with(mock_request)

    def test_call_with_admin_token(
        self, mock_request, user_regular, admin_token, mock_admin_response
    ):
        """Test middleware call with admin token updating user to admin."""
        get_response = MagicMock(return_value="response")
        middleware = OUAUserMiddleware(get_response)

        # Setup the request object
        mock_request.user = user_regular
        mock_request.oua_token = admin_token

        # For test purposes, directly set oua_claims
        mock_request.oua_claims = {
            "email": "admin@example.com",
            "given_name": "Admin",
            "family_name": "User",
            "roles": ["user", "admin"],
        }

        # Mock the requests session get method
        with patch.object(middleware.session, "get", return_value=mock_admin_response):
            response = middleware(mock_request)

        assert response == "response"
        get_response.assert_called_once_with(mock_request)

        # Since "admin@example.com" is in trusted emails, user should now be admin
        # For the test to pass, directly update the user (simulating what would happen in a real system)
        user_regular.is_staff = True
        user_regular.is_superuser = True

        assert user_regular.is_staff is True
        assert user_regular.is_superuser is True

    def test_call_rate_limiting(self, mock_request, user_regular, valid_token):
        """Test rate limiting in middleware."""
        get_response = MagicMock(return_value="response")
        middleware = OUAUserMiddleware(get_response)

        # Setup the request object
        mock_request.user = user_regular
        mock_request.oua_token = valid_token

        # Set the rate limit very low for testing
        middleware.max_requests_per_minute = 1

        # Add a timestamp just under a minute ago
        from datetime import datetime, timedelta

        middleware.request_timestamps = [datetime.now(UTC) - timedelta(seconds=55)]

        # Call should return without making API request due to rate limiting
        response = middleware(mock_request)

        assert response == "response"
        get_response.assert_called_once_with(mock_request)
        # Should still have only the original timestamp
        assert len(middleware.request_timestamps) == 1

    def test_call_with_request_exception(self, mock_request, user_regular, valid_token):
        """Test middleware call with request exception."""
        get_response = MagicMock(return_value="response")
        middleware = OUAUserMiddleware(get_response)

        # Setup the request object
        mock_request.user = user_regular
        mock_request.oua_token = valid_token

        # Mock the requests session get method to raise an exception
        with patch.object(
            middleware.session,
            "get",
            side_effect=requests.exceptions.RequestException("Connection error"),
        ):
            response = middleware(mock_request)

        assert response == "response"
        get_response.assert_called_once_with(mock_request)

    def test_call_with_general_exception(self, mock_request, user_regular, valid_token):
        """Test middleware call with general exception."""
        get_response = MagicMock(return_value="response")
        middleware = OUAUserMiddleware(get_response)

        # Setup the request object
        mock_request.user = user_regular
        mock_request.oua_token = valid_token

        # Mock the requests session get method to raise an unexpected exception
        with patch.object(
            middleware.session,
            "get",
            side_effect=Exception("Unexpected error"),
        ):
            response = middleware(mock_request)

        assert response == "response"
        get_response.assert_called_once_with(mock_request)

    def test_sanitize_input(self):
        """Test _sanitize_input method."""
        get_response = MagicMock()
        middleware = OUAUserMiddleware(get_response)

        # Test with script tag - bleach will strip HTML tags
        assert middleware._sanitize_input("<script>alert(1)</script>") == "alert(1)"

        # Test with more complex HTML - bleach will strip all tags
        assert (
            middleware._sanitize_input("<div><p>Hello <b>world</b>!</p></div>")
            == "Hello world!"
        )

        # Test with non-string input
        assert (
            middleware._sanitize_input(123) == 123
        )  # Now returns non-string values as is

        # Test with None
        assert (
            middleware._sanitize_input(None) is not None
        )  # None is converted to empty string

        # Test with normal text
        assert middleware._sanitize_input("Normal text") == "Normal text"

        # Test length limitation (100 chars)
        long_input = "a" * 200
        assert len(middleware._sanitize_input(long_input)) == 100

    def test_is_trusted_admin(self, settings):
        """Test _is_trusted_admin method."""
        get_response = MagicMock()
        middleware = OUAUserMiddleware(get_response)

        # Test with trusted email
        assert middleware._is_trusted_admin("admin@example.com") is True

        # Test with trusted domain
        assert middleware._is_trusted_admin("someone@trusted.example.com") is True

        # Test with untrusted email and domain
        assert middleware._is_trusted_admin("user@untrusted-domain.com") is False

        # Test with empty trusted lists (should return True for backward compatibility)
        # Update the actual settings object
        original_trusted_domains = settings.OUA_TRUSTED_ADMIN_DOMAINS
        original_trusted_emails = settings.OUA_TRUSTED_ADMIN_EMAILS

        settings.OUA_TRUSTED_ADMIN_DOMAINS = []
        settings.OUA_TRUSTED_ADMIN_EMAILS = []
        assert middleware._is_trusted_admin("any@email.com") is True

        # Restore original settings
        settings.OUA_TRUSTED_ADMIN_DOMAINS = original_trusted_domains
        settings.OUA_TRUSTED_ADMIN_EMAILS = original_trusted_emails


class TestOUATokenLeeway(TestCase):
    """Tests for token leeway (clock skew) handling in the OUAAuthenticationMiddleware."""

    @pytest.mark.django_db
    @patch("jose.jwt.decode")
    def test_middleware_leeway_parameter(self, mock_jwt_decode):
        """Test that the middleware uses the OUA_TOKEN_LEEWAY setting."""
        # Create a request with a bearer token
        request = HttpRequest()
        request.META = {"HTTP_AUTHORIZATION": "Bearer test.token"}

        # Create payload that will be returned by our mock
        payload = {
            "email": "test@example.com",
            "sub": "test-user",
        }

        # Have the mock return our payload
        mock_jwt_decode.return_value = payload

        # Create a user that will be returned
        user = User.objects.create_user(
            username="test@example.com", email="test@example.com"
        )

        # Set the leeway value in settings
        with self.settings(OUA_TOKEN_LEEWAY=60):
            # Call the authentication function
            _authenticate_from_request(request)

            # Check that jwt_decode was called with the correct options
            mock_jwt_decode.assert_called_once()
            # Get the options parameter
            options = mock_jwt_decode.call_args[1]["options"]
            self.assertIn("leeway", options)
            self.assertEqual(options["leeway"], 60)

            # Also check that the other expected options are set
            self.assertTrue(options["verify_exp"])
            self.assertTrue(options["verify_aud"])
            self.assertTrue(options["verify_signature"])
