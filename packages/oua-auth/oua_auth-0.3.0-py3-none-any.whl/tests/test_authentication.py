"""Tests for OUAJWTAuthentication."""

import pytest
from unittest.mock import MagicMock, patch
from rest_framework.exceptions import AuthenticationFailed
import logging
import uuid
from datetime import datetime, timedelta, UTC
from django.utils import timezone
from django.conf import settings
import jwt
import hashlib
import time
from django.core.cache import cache

from oua_auth.authentication import OUAJWTAuthentication


# Add pytest.mark.django_db to the entire class
@pytest.mark.django_db
class TestOUAJWTAuthentication:
    """Tests for OUAJWTAuthentication."""

    @pytest.fixture(autouse=True)
    def clear_cache(self):
        """Clear the cache before and after each test."""
        # Clear any existing entries in the cache
        cache.clear()
        yield
        # Clean up the cache after the test
        cache.clear()

    def test_init(self):
        """Test authentication class initialization."""
        auth = OUAJWTAuthentication()
        assert auth.token_signing_key == "test-signing-key"
        assert auth.trusted_admin_domains == ["trusted.example.com"]
        assert "admin@example.com" in auth.trusted_admin_emails
        assert auth.internal_token_lifetime == 3600
        assert auth.max_failures == getattr(settings, "OUA_MAX_AUTH_FAILURES", 5)
        assert auth.failure_window == getattr(settings, "OUA_AUTH_FAILURE_WINDOW", 300)
        # Check cache-related attributes
        assert auth.cache_prefix == "oua_auth_failure"
        assert auth.cache_timeout == getattr(
            settings, "OUA_RATELIMIT_CACHE_TIMEOUT", auth.failure_window
        )

    def test_authenticate_no_auth_header(self, drf_request):
        """Test authenticate method with no auth header."""
        auth = OUAJWTAuthentication()

        result = auth.authenticate(drf_request)

        assert result is None

    def test_authenticate_with_valid_token(
        self, drf_request, valid_token, jwt_payload_regular, mocker
    ):
        """Test authenticate method with valid token."""
        auth = OUAJWTAuthentication()

        # Need to use HTTP_ prefix for DRF request
        drf_request._request.META["HTTP_AUTHORIZATION"] = f"Bearer {valid_token}"

        # Mock the internal token generation
        mock_generate = mocker.patch.object(
            auth, "_generate_internal_token", return_value="internal-token"
        )

        # Mock rate limiting methods
        mocker.patch.object(auth, "_get_client_ip", return_value="127.0.0.1")
        mocker.patch.object(auth, "_is_rate_limited", return_value=False)
        mocker.patch.object(auth, "_is_token_blacklisted", return_value=False)
        mocker.patch.object(auth, "_log_auth_success", return_value=None)

        user, token = auth.authenticate(drf_request)

        assert user is not None
        assert user.email == "user@example.com"
        assert token == "internal-token"
        assert drf_request.oua_token == valid_token
        assert drf_request.oua_claims == jwt_payload_regular
        assert drf_request.internal_token == "internal-token"
        mock_generate.assert_called_once()

    def test_authenticate_with_admin_token(
        self, drf_request, admin_token, jwt_payload_admin, mocker
    ):
        """Test authenticate method with admin token from trusted email."""
        auth = OUAJWTAuthentication()

        # Need to use HTTP_ prefix for DRF request
        drf_request._request.META["HTTP_AUTHORIZATION"] = f"Bearer {admin_token}"

        # Mock the internal token generation
        mock_generate = mocker.patch.object(
            auth, "_generate_internal_token", return_value="internal-token"
        )

        # Mock rate limiting methods
        mocker.patch.object(auth, "_get_client_ip", return_value="127.0.0.1")
        mocker.patch.object(auth, "_is_rate_limited", return_value=False)
        mocker.patch.object(auth, "_is_token_blacklisted", return_value=False)
        mocker.patch.object(auth, "_log_auth_success", return_value=None)

        user, token = auth.authenticate(drf_request)

        assert user is not None
        assert user.email == "admin@example.com"
        assert user.is_staff is True
        assert user.is_superuser is True
        assert token == "internal-token"
        assert drf_request.oua_token == admin_token
        assert drf_request.oua_claims == jwt_payload_admin
        assert drf_request.internal_token == "internal-token"
        mock_generate.assert_called_once()

    def test_authenticate_with_untrusted_admin_token(
        self, drf_request, untrusted_admin_token, jwt_payload_admin_untrusted, mocker
    ):
        """Test authenticate method with admin token from untrusted email."""
        auth = OUAJWTAuthentication()

        # Need to use HTTP_ prefix for DRF request
        drf_request._request.META["HTTP_AUTHORIZATION"] = (
            f"Bearer {untrusted_admin_token}"
        )

        # Mock the internal token generation
        mock_generate = mocker.patch.object(
            auth, "_generate_internal_token", return_value="internal-token"
        )

        # Mock rate limiting methods
        mocker.patch.object(auth, "_get_client_ip", return_value="127.0.0.1")
        mocker.patch.object(auth, "_is_rate_limited", return_value=False)
        mocker.patch.object(auth, "_is_token_blacklisted", return_value=False)
        mocker.patch.object(auth, "_log_auth_success", return_value=None)

        user, token = auth.authenticate(drf_request)

        assert user is not None
        assert user.email == "admin@untrusted-domain.com"
        # Should not have admin privileges
        assert user.is_staff is False
        assert user.is_superuser is False
        assert token == "internal-token"
        assert drf_request.oua_token == untrusted_admin_token
        assert drf_request.oua_claims == jwt_payload_admin_untrusted
        assert drf_request.internal_token == "internal-token"
        mock_generate.assert_called_once()

    def test_authenticate_with_trusted_domain(
        self, drf_request, trusted_domain_token, jwt_payload_trusted_domain, mocker
    ):
        """Test authenticate method with token from trusted domain."""
        auth = OUAJWTAuthentication()

        # Need to use HTTP_ prefix for DRF request
        drf_request._request.META["HTTP_AUTHORIZATION"] = (
            f"Bearer {trusted_domain_token}"
        )

        # Mock the internal token generation
        mock_generate = mocker.patch.object(
            auth, "_generate_internal_token", return_value="internal-token"
        )

        # Mock rate limiting methods
        mocker.patch.object(auth, "_get_client_ip", return_value="127.0.0.1")
        mocker.patch.object(auth, "_is_rate_limited", return_value=False)
        mocker.patch.object(auth, "_is_token_blacklisted", return_value=False)
        mocker.patch.object(auth, "_log_auth_success", return_value=None)

        user, token = auth.authenticate(drf_request)

        assert user is not None
        assert user.email == "user@trusted.example.com"
        # Should have admin privileges due to trusted domain
        assert user.is_staff is True
        assert user.is_superuser is True
        assert token == "internal-token"
        mock_generate.assert_called_once()

    def test_authenticate_expired_token(self, drf_request, expired_token, mocker):
        """Test authenticate method with expired token."""
        auth = OUAJWTAuthentication()

        # Need to use HTTP_ prefix for DRF request
        drf_request._request.META["HTTP_AUTHORIZATION"] = f"Bearer {expired_token}"

        # Mock rate limiting methods
        mocker.patch.object(auth, "_get_client_ip", return_value="127.0.0.1")
        mocker.patch.object(auth, "_is_rate_limited", return_value=False)
        mocker.patch.object(auth, "_is_token_blacklisted", return_value=False)
        mocker.patch.object(auth, "_record_auth_failure", return_value=None)

        with pytest.raises(AuthenticationFailed) as excinfo:
            auth.authenticate(drf_request)

        assert "Token expired" in str(excinfo.value)

    def test_authenticate_malformed_token(self, drf_request, malformed_token, mocker):
        """Test authenticate method with malformed token (missing email)."""
        auth = OUAJWTAuthentication()

        # Need to use HTTP_ prefix for DRF request
        drf_request._request.META["HTTP_AUTHORIZATION"] = f"Bearer {malformed_token}"

        # Mock rate limiting methods
        mocker.patch.object(auth, "_get_client_ip", return_value="127.0.0.1")
        mocker.patch.object(auth, "_is_rate_limited", return_value=False)
        mocker.patch.object(auth, "_is_token_blacklisted", return_value=False)
        mocker.patch.object(auth, "_record_auth_failure", return_value=None)

        with pytest.raises(AuthenticationFailed) as excinfo:
            auth.authenticate(drf_request)

        assert "Invalid token: no email claim" in str(excinfo.value)

    def test_authenticate_invalid_email_format(
        self, drf_request, invalid_email_token, mocker
    ):
        """Test authenticate method with invalid email format."""
        auth = OUAJWTAuthentication()

        # Need to use HTTP_ prefix for DRF request
        drf_request._request.META["HTTP_AUTHORIZATION"] = (
            f"Bearer {invalid_email_token}"
        )

        # Mock rate limiting methods
        mocker.patch.object(auth, "_get_client_ip", return_value="127.0.0.1")
        mocker.patch.object(auth, "_is_rate_limited", return_value=False)
        mocker.patch.object(auth, "_is_token_blacklisted", return_value=False)
        mocker.patch.object(auth, "_record_auth_failure", return_value=None)

        with pytest.raises(AuthenticationFailed) as excinfo:
            auth.authenticate(drf_request)

        assert "Invalid email format in token" in str(excinfo.value)

    def test_authenticate_header(self):
        """Test authenticate_header method."""
        auth = OUAJWTAuthentication()
        request = MagicMock()

        result = auth.authenticate_header(request)

        assert result == "Bearer"

    def test_generate_internal_token(self, user_regular, jwt_payload_regular):
        """Test the internal token generation."""
        auth = OUAJWTAuthentication()

        internal_token = auth._generate_internal_token(
            user_regular, jwt_payload_regular
        )

        assert isinstance(internal_token, str)
        assert len(internal_token) > 0

    def test_generate_internal_token_exception(
        self, user_regular, jwt_payload_regular, mocker
    ):
        """Test the internal token generation with exception."""
        auth = OUAJWTAuthentication()

        # Mock jwt.encode to raise an exception
        mocker.patch(
            "oua_auth.authentication.jwt.encode",
            side_effect=Exception("Token generation error"),
        )

        with pytest.raises(Exception):
            auth._generate_internal_token(user_regular, jwt_payload_regular)

    def test_sanitize_input(self):
        """Test _sanitize_input method."""
        auth = OUAJWTAuthentication()

        # Test with script tag - bleach will strip HTML tags
        assert auth._sanitize_input("<script>alert(1)</script>") == "alert(1)"

        # Test with more complex HTML - bleach will strip all tags
        assert (
            auth._sanitize_input("<div><p>Hello <b>world</b>!</p></div>")
            == "Hello world!"
        )

        # Test with non-string input
        assert auth._sanitize_input(123) == 123  # Now returns non-string values as is

        # Test with None
        assert auth._sanitize_input(None) == None  # Returns None as is

        # Test with normal text
        assert auth._sanitize_input("Normal text") == "Normal text"

        # Test length limitation (100 chars)
        long_input = "a" * 200
        assert len(auth._sanitize_input(long_input)) == 100

    def test_is_trusted_admin(self):
        """Test _is_trusted_admin method."""
        auth = OUAJWTAuthentication()

        # Test with trusted email
        assert auth._is_trusted_admin("admin@example.com") is True

        # Test with trusted domain
        assert auth._is_trusted_admin("someone@trusted.example.com") is True

        # Test with untrusted email and domain
        assert auth._is_trusted_admin("user@untrusted-domain.com") is False

        # Test with empty trusted lists (should return True for backward compatibility)
        auth.trusted_admin_domains = []
        auth.trusted_admin_emails = []
        assert auth._is_trusted_admin("any@email.com") is True

    def test_authenticate_exception(self, drf_request, mocker):
        """Test authenticate method with exception."""
        auth = OUAJWTAuthentication()

        # Setup request with authorization header
        drf_request._request.META["HTTP_AUTHORIZATION"] = "Bearer some.token.here"

        # Mock rate limiting methods
        mocker.patch.object(auth, "_get_client_ip", return_value="127.0.0.1")
        mocker.patch.object(auth, "_is_rate_limited", return_value=False)
        mocker.patch.object(auth, "_is_token_blacklisted", return_value=False)
        mocker.patch.object(auth, "_record_auth_failure", return_value=None)

        # Mock jwt.decode to raise an exception
        mocker.patch(
            "oua_auth.authentication.jwt.decode",
            side_effect=Exception("Authentication error"),
        )

        with pytest.raises(AuthenticationFailed) as excinfo:
            auth.authenticate(drf_request)

        assert "Authentication failed" in str(excinfo.value)

    def test_authenticate_rate_limited(self, drf_request, mocker):
        """Test authenticate method with rate limiting."""
        auth = OUAJWTAuthentication()

        # Setup request with authorization header
        drf_request._request.META["HTTP_AUTHORIZATION"] = "Bearer some.token.here"

        # Mock the rate limiting logic to return True (rate limited)
        mocker.patch.object(auth, "_get_client_ip", return_value="127.0.0.1")
        mocker.patch.object(auth, "_is_rate_limited", return_value=True)

        with pytest.raises(AuthenticationFailed) as excinfo:
            auth.authenticate(drf_request)

        assert "Too many failed attempts. Please try again later." in str(excinfo.value)

    def test_get_client_ip(self, drf_request):
        """Test _get_client_ip method."""
        auth = OUAJWTAuthentication()

        # Mock the request object
        drf_request._request.META["HTTP_X_FORWARDED_FOR"] = "1.2.3.4, 5.6.7.8"
        drf_request._request.META["REMOTE_ADDR"] = "9.8.7.6"

        ip = auth._get_client_ip(drf_request)

        assert ip == "1.2.3.4"

    def test_is_rate_limited(self):
        """Test _is_rate_limited method."""
        auth = OUAJWTAuthentication()
        # Create a mock request instead of just passing an IP string
        mock_request = MagicMock()
        mock_request.META = {"REMOTE_ADDR": "1.2.3.4"}
        mock_request.path = "/api/test"

        # Mock cache behavior
        with patch("oua_auth.authentication.cache") as mock_cache:
            # Return empty list instead of None
            mock_cache.get.return_value = []

            # Should not be rate limited with empty failure list
            assert auth._is_rate_limited(mock_request) is False

            # Test with failures but below threshold
            mock_cache.get.return_value = [time.time() - 10 for _ in range(3)]
            assert auth._is_rate_limited(mock_request) is False

            # Test with failures above threshold
            auth.max_failures = 5
            mock_cache.get.return_value = [time.time() - 10 for _ in range(6)]
            assert auth._is_rate_limited(mock_request) is True

    def test_record_auth_failure(self):
        """Test _record_auth_failure method."""
        auth = OUAJWTAuthentication()
        ip = "1.2.3.4"
        cache_key = f"{auth.cache_prefix}:{ip}"

        # Make sure there are no existing failures
        with patch("oua_auth.authentication.cache") as mock_cache:
            # Configure cache mock to return a list
            mock_cache.get.return_value = []

            # Record a failure
            auth._record_auth_failure(ip)

            # Verify cache.get and cache.set were called
            mock_cache.get.assert_called_once()
            mock_cache.set.assert_called_once()

            # Verify that a timestamp was added to the failures list
            failures_arg = mock_cache.set.call_args[0][1]
            assert len(failures_arg) == 1
            # Verify the timestamp is recent
            assert time.time() - failures_arg[0] < 5  # Within last 5 seconds

    def test_authenticate_with_valid_token_additional_validation(
        self, drf_request, valid_token, jwt_payload_regular, mocker
    ):
        """Test authenticate method with valid token and additional validation."""
        auth = OUAJWTAuthentication()

        # Need to use HTTP_ prefix for DRF request
        drf_request._request.META["HTTP_AUTHORIZATION"] = f"Bearer {valid_token}"

        # Mock the internal token generation and validation methods
        mock_generate = mocker.patch.object(
            auth, "_generate_internal_token", return_value="internal-token"
        )
        mocker.patch.object(auth, "_get_client_ip", return_value="127.0.0.1")
        mocker.patch.object(auth, "_is_rate_limited", return_value=False)
        mocker.patch.object(auth, "_is_token_blacklisted", return_value=False)
        mocker.patch.object(auth, "_log_auth_success", return_value=None)

        # Mock jwt.decode for the additional validation
        mocker.patch(
            "tests.test_authentication.jwt.decode",
            return_value={"iat": int(datetime.now(UTC).timestamp())},
        )

        user, token = auth.authenticate(drf_request)

        assert user is not None
        assert user.email == "user@example.com"
        assert token == "internal-token"
        assert drf_request.oua_token == valid_token
        assert drf_request.oua_claims == jwt_payload_regular
        assert drf_request.internal_token == "internal-token"
        mock_generate.assert_called_once()

    def test_is_token_blacklisted(self, valid_token, mocker):
        """Test _is_token_blacklisted method."""
        auth = OUAJWTAuthentication()

        # Mock database check to first return False then True
        is_blacklisted_mock = mocker.patch(
            "oua_auth.models.BlacklistedToken.is_token_blacklisted",
            return_value=False,
        )

        # Initially, token should not be blacklisted
        assert auth._is_token_blacklisted(valid_token) is False
        is_blacklisted_mock.assert_called_once_with(valid_token)

        # Change mock to return True
        is_blacklisted_mock.return_value = True
        is_blacklisted_mock.reset_mock()

        # Now token should be blacklisted
        assert auth._is_token_blacklisted(valid_token) is True
        is_blacklisted_mock.assert_called_once_with(valid_token)

    def test_revoke_token(self, valid_token, mocker):
        """Test revoke_token method."""
        # Mock the database add_token_to_blacklist method
        add_to_blacklist_mock = mocker.patch(
            "oua_auth.models.BlacklistedToken.add_token_to_blacklist",
            return_value=mocker.MagicMock(),
        )

        # Mock jwt.decode to return a payload with exp
        exp_time = int(time.time()) + 3600  # 1 hour in future
        mock_payload = {"exp": exp_time}
        mocker.patch("oua_auth.authentication.jwt.decode", return_value=mock_payload)

        # This is testing a class method
        result = OUAJWTAuthentication.revoke_token(
            valid_token, blacklisted_by="test", reason="Testing revocation"
        )

        # Should return True
        assert result is True

        # Should have called add_token_to_blacklist
        add_to_blacklist_mock.assert_called_once()
        call_args = add_to_blacklist_mock.call_args[1]
        assert call_args["token"] == valid_token
        assert call_args["blacklisted_by"] == "test"
        assert call_args["reason"] == "Testing revocation"

    def test_log_auth_success(
        self, drf_request, user_regular, jwt_payload_regular, mocker
    ):
        """Test _log_auth_success method."""
        auth = OUAJWTAuthentication()

        # Mock the instance logger instead of the global logger
        mock_logger = mocker.MagicMock()
        auth.log = mock_logger

        # Mock client IP
        mocker.patch.object(auth, "_get_client_ip", return_value="127.0.0.1")

        # Setup request user-agent
        drf_request._request.META["HTTP_USER_AGENT"] = "Test User Agent"

        # Call the method
        auth._log_auth_success(drf_request, user_regular, jwt_payload_regular)

        # Verify logger was called
        mock_logger.info.assert_called_once()

        # Verify data in call
        call_args = mock_logger.info.call_args[0]
        assert "Authentication successful" in call_args[0]

        # Verify extra data
        extra_data = mock_logger.info.call_args[1]["extra"]["audit"]
        assert extra_data["event"] == "authentication_success"
        assert extra_data["user_id"] == user_regular.id
        assert extra_data["user_email"] == user_regular.email
        assert extra_data["client_ip"] == "127.0.0.1"
        assert extra_data["user_agent"] == "Test User Agent"
