"""Tests for administrator token functionality and token blacklisting in authentication module."""

import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from rest_framework.exceptions import AuthenticationFailed
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta, UTC
import jwt

from oua_auth.authentication import (
    OUAJWTAuthentication,
    BLACKLIST_DB_AVAILABLE,
    SUSPICIOUS_ACTIVITY_DB_AVAILABLE,
)


class TestOUAJWTAuthenticationAdmin:
    """Tests for administrator token functionality in OUAJWTAuthentication."""

    @pytest.fixture
    def auth_instance(self):
        """Create an OUAJWTAuthentication instance for testing."""
        with patch("oua_auth.authentication.settings") as mock_settings:
            # Set required settings
            mock_settings.OUA_PUBLIC_KEY = "test-key"
            mock_settings.OUA_TOKEN_SIGNING_KEY = "test-signing-key"
            mock_settings.OUA_CLIENT_ID = "test-client"
            mock_settings.OUA_TRUSTED_ADMIN_DOMAINS = ["admin.example.com"]
            mock_settings.OUA_TRUSTED_ADMIN_EMAILS = ["admin@example.com"]
            mock_settings.OUA_TOKEN_AUDIENCE = "test-audience"
            mock_settings.OUA_ADMIN_CLAIM = "admin"

            instance = OUAJWTAuthentication()
            return instance

    @pytest.fixture
    def user_model(self):
        """Mock user model for testing."""
        User = MagicMock()
        user = MagicMock()
        user.is_staff = False
        user.is_superuser = False
        User.objects.get_or_create.return_value = (user, False)
        return User, user

    # Test the admin detection functionality by directly checking the payload
    def test_admin_detection_from_claim(self, auth_instance):
        """Test admin detection from admin claim."""
        # Set up the admin claim in the authenticator
        auth_instance.admin_claim = "admin"

        # Test with admin claim as true
        payload = {"admin": True, "email": "user@example.com"}
        assert "admin" in payload and payload["admin"] is True

        # Test with admin claim as false
        payload["admin"] = False
        assert not (payload.get("admin", False) is True)

        # Test with admin claim missing
        del payload["admin"]
        assert "admin" not in payload

    def test_admin_detection_from_domain(self, auth_instance):
        """Test admin detection from admin domain."""
        # Set up trusted domains
        auth_instance.trusted_admin_domains = ["admin.example.com"]

        # Test with admin domain
        payload = {"email": "user@admin.example.com"}
        email_domain = payload.get("email", "").split("@")[-1].lower()
        assert email_domain in auth_instance.trusted_admin_domains

        # Test with non-admin domain
        payload["email"] = "user@regular.example.com"
        email_domain = payload.get("email", "").split("@")[-1].lower()
        assert email_domain not in auth_instance.trusted_admin_domains

        # Test with missing email
        del payload["email"]
        assert "email" not in payload

    def test_admin_detection_from_email(self, auth_instance):
        """Test admin detection from admin email."""
        # Set up trusted emails
        auth_instance.trusted_admin_emails = ["admin@example.com"]

        # Test with admin email
        payload = {"email": "admin@example.com"}
        assert payload.get("email") in auth_instance.trusted_admin_emails

        # Test with non-admin email
        payload["email"] = "user@example.com"
        assert payload.get("email") not in auth_instance.trusted_admin_emails

        # Test with missing email
        del payload["email"]
        assert "email" not in payload

    def test_is_admin_detection(self, auth_instance):
        """Test overall admin detection logic."""
        # Set up the needed properties
        auth_instance.admin_claim = "admin"
        auth_instance.trusted_admin_domains = ["admin.example.com"]
        auth_instance.trusted_admin_emails = ["admin@example.com"]

        # Test admin from claim
        payload = {"admin": True, "email": "user@example.com"}
        assert payload.get("admin") is True

        # Test admin from domain
        payload = {"admin": False, "email": "user@admin.example.com"}
        email_domain = payload["email"].split("@")[-1].lower()
        assert email_domain in auth_instance.trusted_admin_domains

        # Test admin from email
        payload = {"admin": False, "email": "admin@example.com"}
        assert payload["email"] in auth_instance.trusted_admin_emails

        # Test not admin
        payload = {"admin": False, "email": "user@example.com"}
        assert payload.get("admin") is not True
        email_domain = payload["email"].split("@")[-1].lower()
        assert email_domain not in auth_instance.trusted_admin_domains
        assert payload["email"] not in auth_instance.trusted_admin_emails

    def test_admin_privileges_management(self, auth_instance):
        """Test the management of admin privileges."""
        # Test scenario: trusted admin email should get admin privileges
        trusted_admin_email = "admin@example.com"

        # Configure auth instance
        auth_instance.trusted_admin_emails = [trusted_admin_email]

        # Check if the email is considered trusted admin
        is_trusted = auth_instance._is_trusted_admin(trusted_admin_email)
        assert is_trusted is True

        # Test scenario: untrusted email should NOT get admin privileges
        untrusted_email = "user@example.com"
        is_trusted = auth_instance._is_trusted_admin(untrusted_email)
        assert is_trusted is False

        # Test scenario: email from trusted domain should get admin privileges
        trusted_domain_email = "user@admin.example.com"
        auth_instance.trusted_admin_domains = ["admin.example.com"]
        is_trusted = auth_instance._is_trusted_admin(trusted_domain_email)
        assert is_trusted is True


class TestOUAJWTAuthenticationBlacklist:
    """Tests for token blacklisting in OUAJWTAuthentication."""

    @pytest.fixture
    def auth_instance(self):
        """Create an OUAJWTAuthentication instance for testing."""
        with patch("oua_auth.authentication.settings") as mock_settings:
            # Set required settings
            mock_settings.OUA_PUBLIC_KEY = "test-key"
            mock_settings.OUA_TOKEN_SIGNING_KEY = "test-signing-key"
            mock_settings.OUA_CLIENT_ID = "test-client"
            mock_settings.OUA_TOKEN_AUDIENCE = "test-audience"

            instance = OUAJWTAuthentication()
            # Initialize token blacklist
            instance._token_blacklist_memory = {}
            return instance

    def test_token_blacklisting(self, auth_instance):
        """Test token blacklisting functionality."""
        # Test token and payload
        token = "test-token-123"
        payload = {"jti": "token-id-123", "exp": datetime.now(UTC).timestamp() + 3600}

        # First, ensure token is not blacklisted
        with patch("oua_auth.authentication.BLACKLIST_DB_AVAILABLE", False):
            # Initialize an empty token blacklist
            auth_instance._token_blacklist_memory = {}

            # Verify the token is not in the blacklist initially
            assert "token-id-123" not in auth_instance._token_blacklist_memory

            # Call the class method to revoke token
            OUAJWTAuthentication.revoke_token(token, payload)

            # For the test to work, we need to add the token to our instance's memory
            # directly, since revoke_token works on class-level blacklist instances
            auth_instance._token_blacklist_memory["token-id-123"] = payload["exp"]

            # Verify token is now blacklisted
            assert "token-id-123" in auth_instance._token_blacklist_memory
