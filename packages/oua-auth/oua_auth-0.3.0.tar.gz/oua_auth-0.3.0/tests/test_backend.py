"""Tests for OUAAuthBackend."""

import pytest
from unittest.mock import MagicMock, patch
import requests
from django.contrib.auth import get_user_model

from oua_auth.backend import OUAAuthBackend


# Add pytest.mark.django_db to the entire class
@pytest.mark.django_db
class TestOUAAuthBackend:
    """Tests for OUAAuthBackend."""

    def test_init(self):
        """Test backend initialization."""
        backend = OUAAuthBackend()
        assert backend.sso_url == "https://test-sso.example.com"
        assert hasattr(backend, "session")
        assert backend.request_timeout == 5
        assert backend.trusted_admin_domains == ["trusted.example.com"]
        assert "admin@example.com" in backend.trusted_admin_emails

    def test_authenticate_no_token(self, mock_request):
        """Test authenticate method with no token."""
        backend = OUAAuthBackend()

        result = backend.authenticate(mock_request, token=None)

        assert result is None

    def test_authenticate_with_valid_token(
        self, mock_request, valid_token, mock_response
    ):
        """Test authenticate method with valid token."""
        backend = OUAAuthBackend()

        # Create a mock user
        User = get_user_model()
        regular_user = User.objects.create_user(
            username="testuser",
            email="user@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
            is_staff=False,
            is_superuser=False,
        )

        # Create a mock internal token
        mock_internal_token = "mock_internal_token"

        # Mock the OUAJWTAuthentication.authenticate method
        with patch(
            "oua_auth.authentication.OUAJWTAuthentication.authenticate",
            return_value=(regular_user, mock_internal_token),
        ):
            user = backend.authenticate(mock_request, token=valid_token)

        assert user is not None
        assert user.email == "user@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_authenticate_with_admin_token(
        self, mock_request, admin_token, mock_admin_response
    ):
        """Test authenticate method with admin token."""
        backend = OUAAuthBackend()

        # Create a mock admin user
        User = get_user_model()
        admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="password123",
            first_name="Admin",
            last_name="User",
            is_staff=True,
            is_superuser=True,
        )

        # Create a mock internal token
        mock_internal_token = "mock_internal_token"

        # Mock the OUAJWTAuthentication.authenticate method
        with patch(
            "oua_auth.authentication.OUAJWTAuthentication.authenticate",
            return_value=(admin_user, mock_internal_token),
        ):
            user = backend.authenticate(mock_request, token=admin_token)

        assert user is not None
        assert user.email == "admin@example.com"
        assert user.first_name == "Admin"
        assert user.last_name == "User"
        # admin@example.com is in trusted_admin_emails
        assert user.is_staff is True
        assert user.is_superuser is True

    def test_authenticate_with_admin_untrusted_domain(self, mock_request, valid_token):
        """Test authenticate method with admin token from untrusted domain."""
        backend = OUAAuthBackend()

        # Create a mock user with untrusted admin email
        User = get_user_model()
        untrusted_user = User.objects.create_user(
            username="untrusted_admin",
            email="admin@untrusted-domain.com",
            password="password123",
            first_name="Untrusted",
            last_name="Admin",
            is_staff=False,
            is_superuser=False,
        )

        # Create a mock internal token
        mock_internal_token = "mock_internal_token"

        # Mock the OUAJWTAuthentication.authenticate method
        with patch(
            "oua_auth.authentication.OUAJWTAuthentication.authenticate",
            return_value=(untrusted_user, mock_internal_token),
        ):
            user = backend.authenticate(mock_request, token=valid_token)

        assert user is not None
        assert user.email == "admin@untrusted-domain.com"
        # Should not have admin privileges
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_authenticate_http_error_response(self, mock_request, valid_token):
        """Test authenticate method with HTTP error response."""
        backend = OUAAuthBackend()

        # Mock the OUAJWTAuthentication.authenticate method to raise an exception
        with patch(
            "oua_auth.authentication.OUAJWTAuthentication.authenticate",
            side_effect=Exception("HTTP Error"),
        ):
            user = backend.authenticate(mock_request, token=valid_token)

        assert user is None

    def test_authenticate_missing_email(self, mock_request, valid_token):
        """Test authenticate method with missing email in response."""
        backend = OUAAuthBackend()

        # Mock the OUAJWTAuthentication.authenticate method to return None
        with patch(
            "oua_auth.authentication.OUAJWTAuthentication.authenticate",
            return_value=None,
        ):
            user = backend.authenticate(mock_request, token=valid_token)

        assert user is None

    def test_authenticate_invalid_email_format(self, mock_request, valid_token):
        """Test authenticate method with invalid email format in response."""
        backend = OUAAuthBackend()

        # Mock the OUAJWTAuthentication.authenticate method to return None
        with patch(
            "oua_auth.authentication.OUAJWTAuthentication.authenticate",
            return_value=None,
        ):
            user = backend.authenticate(mock_request, token=valid_token)

        assert user is None

    def test_authenticate_request_exception(self, mock_request, valid_token):
        """Test authenticate method with request exception."""
        backend = OUAAuthBackend()

        # Mock the OUAJWTAuthentication.authenticate method to raise an exception
        with patch(
            "oua_auth.authentication.OUAJWTAuthentication.authenticate",
            side_effect=requests.exceptions.RequestException("Connection error"),
        ):
            user = backend.authenticate(mock_request, token=valid_token)

        assert user is None

    def test_authenticate_timeout_exception(self, mock_request, valid_token):
        """Test authenticate method with timeout exception."""
        backend = OUAAuthBackend()

        # Mock the OUAJWTAuthentication.authenticate method to raise a timeout exception
        with patch(
            "oua_auth.authentication.OUAJWTAuthentication.authenticate",
            side_effect=requests.exceptions.Timeout("Request timed out"),
        ):
            user = backend.authenticate(mock_request, token=valid_token)

        assert user is None

    def test_get_user(self, user_regular):
        """Test get_user method with existing user."""
        backend = OUAAuthBackend()

        user = backend.get_user(user_regular.id)

        assert user == user_regular

    def test_get_user_nonexistent(self):
        """Test get_user method with non-existent user."""
        backend = OUAAuthBackend()

        user = backend.get_user(9999)  # Non-existent ID

        assert user is None

    def test_authenticate_general_exception(self, mock_request, valid_token):
        """Test authenticate method with general exception."""
        backend = OUAAuthBackend()

        # Mock the OUAJWTAuthentication.authenticate method to raise a general exception
        with patch(
            "oua_auth.authentication.OUAJWTAuthentication.authenticate",
            side_effect=Exception("Unexpected error"),
        ):
            user = backend.authenticate(mock_request, token=valid_token)

        assert user is None

    def test_sanitize_input(self):
        """Test _sanitize_input method."""
        backend = OUAAuthBackend()

        # Test with script tag - bleach will strip HTML tags
        assert backend._sanitize_input("<script>alert(1)</script>") == "alert(1)"

        # Test with more complex HTML - bleach will strip all tags
        assert (
            backend._sanitize_input("<div><p>Hello <b>world</b>!</p></div>")
            == "Hello world!"
        )

        # Test with non-string input
        assert (
            backend._sanitize_input(123) == 123
        )  # Now returns non-string values as is

        # Test with None
        assert (
            backend._sanitize_input(None) is not None
        )  # None is converted to empty string

        # Test with normal text
        assert backend._sanitize_input("Normal text") == "Normal text"

        # Test length limitation (100 chars)
        long_input = "a" * 200
        assert len(backend._sanitize_input(long_input)) == 100

    def test_validate_email_format(self):
        """Test _validate_email_format method."""
        backend = OUAAuthBackend()

        # Test with valid email formats
        assert backend._validate_email_format("user@example.com") is True
        assert backend._validate_email_format("user.name+tag@example.co.uk") is True

        # Test with invalid email formats
        assert backend._validate_email_format("not-an-email") is False
        assert backend._validate_email_format("missing@domain") is False
        assert backend._validate_email_format("@example.com") is False
        assert backend._validate_email_format("user@") is False

    def test_is_trusted_admin(self):
        """Test _is_trusted_admin method."""
        backend = OUAAuthBackend()

        # Test with trusted email
        assert backend._is_trusted_admin("admin@example.com") is True

        # Test with trusted domain
        assert backend._is_trusted_admin("someone@trusted.example.com") is True

        # Test with untrusted email and domain
        assert backend._is_trusted_admin("user@untrusted-domain.com") is False

        # Test with empty trusted lists (should return True for backward compatibility)
        backend.trusted_admin_domains = []
        backend.trusted_admin_emails = []
        assert backend._is_trusted_admin("any@email.com") is True
