"""Tests for BlacklistedToken model and token blacklisting functionality."""

import pytest
from django.utils import timezone
from datetime import timedelta
import hashlib
from jose import jwt
from unittest.mock import patch, MagicMock

from oua_auth.models import BlacklistedToken
from oua_auth.authentication import OUAJWTAuthentication
from oua_auth.token_blacklist import (
    initialize_token_blacklist,
    add_token_to_memory_blacklist,
    is_token_in_memory_blacklist,
    _token_blacklist,
)


@pytest.mark.django_db
class TestBlacklistedToken:
    """Tests for BlacklistedToken model."""

    def test_add_token_to_blacklist(self, valid_token):
        """Test adding a token to the blacklist."""
        # Add token to blacklist with explicit expiration
        expires_at = timezone.now() + timedelta(hours=1)
        blacklisted_token = BlacklistedToken.add_token_to_blacklist(
            token=valid_token,
            expires_at=expires_at,
            blacklisted_by="test_user",
            reason="Testing token blacklisting",
        )

        # Verify the token was added
        assert blacklisted_token.id is not None
        assert (
            blacklisted_token.token_hash
            == hashlib.sha256(valid_token.encode()).hexdigest()
        )
        assert blacklisted_token.expires_at == expires_at
        assert blacklisted_token.blacklisted_by == "test_user"
        assert blacklisted_token.reason == "Testing token blacklisting"

        # Verify the token is found when checking if blacklisted
        assert BlacklistedToken.is_token_blacklisted(valid_token) is True

    def test_add_token_to_blacklist_without_expiry(self, valid_token):
        """Test adding a token to the blacklist without specifying expiration."""
        # Add token to blacklist without explicit expiration
        blacklisted_token = BlacklistedToken.add_token_to_blacklist(
            token=valid_token,
        )

        # Verify the token was added with a default expiration
        assert blacklisted_token.id is not None
        assert (
            blacklisted_token.token_hash
            == hashlib.sha256(valid_token.encode()).hexdigest()
        )

        # Default expiration should be about 24 hours from now
        time_diff = blacklisted_token.expires_at - timezone.now()
        assert time_diff.days == 0  # Should be less than 1 day
        assert time_diff.seconds > 23 * 3600  # Should be at least 23 hours

        # Verify the token is found when checking if blacklisted
        assert BlacklistedToken.is_token_blacklisted(valid_token) is True

    def test_token_not_in_blacklist(self, valid_token, admin_token):
        """Test checking for a token that is not blacklisted."""
        # Blacklist one token
        BlacklistedToken.add_token_to_blacklist(token=valid_token)

        # Check a different token
        assert BlacklistedToken.is_token_blacklisted(admin_token) is False

    def test_clean_expired_tokens(self, valid_token):
        """Test cleaning expired tokens from the blacklist."""
        # Add an expired token
        expired_time = timezone.now() - timedelta(minutes=1)
        BlacklistedToken.add_token_to_blacklist(
            token=valid_token,
            expires_at=expired_time,
        )

        # Verify token was added
        token_hash = hashlib.sha256(valid_token.encode()).hexdigest()
        assert BlacklistedToken.objects.filter(token_hash=token_hash).exists()

        # Clean expired tokens
        BlacklistedToken.clean_expired_tokens()

        # Verify token was removed
        assert not BlacklistedToken.objects.filter(token_hash=token_hash).exists()

    def test_automatic_cleanup_on_check(self, valid_token):
        """Test that expired tokens are cleaned automatically when checking."""
        # Add an expired token
        expired_time = timezone.now() - timedelta(minutes=1)
        BlacklistedToken.add_token_to_blacklist(
            token=valid_token,
            expires_at=expired_time,
        )

        # Verify token was added
        token_hash = hashlib.sha256(valid_token.encode()).hexdigest()
        assert BlacklistedToken.objects.filter(token_hash=token_hash).exists()

        # Check if token is blacklisted (should clean expired tokens)
        assert BlacklistedToken.is_token_blacklisted(valid_token) is False

        # Verify token was removed
        assert not BlacklistedToken.objects.filter(token_hash=token_hash).exists()


@pytest.mark.django_db
class TestOUAJWTAuthenticationWithBlacklist:
    """Tests for OUAJWTAuthentication with database token blacklist."""

    def test_authenticate_with_blacklisted_token(
        self, drf_request, valid_token, mocker
    ):
        """Test authenticate method with a blacklisted token."""
        # Add token to blacklist
        BlacklistedToken.add_token_to_blacklist(token=valid_token)

        # Setup authentication
        auth = OUAJWTAuthentication()
        drf_request._request.META["HTTP_AUTHORIZATION"] = f"Bearer {valid_token}"

        # Mock rate limiting methods
        mocker.patch.object(auth, "_get_client_ip", return_value="127.0.0.1")
        mocker.patch.object(auth, "_is_rate_limited", return_value=False)

        # Try to authenticate with blacklisted token
        with pytest.raises(Exception) as excinfo:
            auth.authenticate(drf_request)

        # Should fail with appropriate message
        assert "Token has been revoked" in str(excinfo.value)

    def test_revoke_token_class_method(self, valid_token):
        """Test OUAJWTAuthentication.revoke_token class method."""
        # Revoke a token
        result = OUAJWTAuthentication.revoke_token(
            token=valid_token,
            blacklisted_by="test_user",
            reason="Testing revocation",
        )

        # Should return True for success
        assert result is True

        # Token should be in the blacklist
        token_hash = hashlib.sha256(valid_token.encode()).hexdigest()
        blacklisted_token = BlacklistedToken.objects.get(token_hash=token_hash)

        # Check blacklisted_by and reason were saved
        assert blacklisted_token.blacklisted_by == "test_user"
        assert blacklisted_token.reason == "Testing revocation"

    def test_revoke_token_with_expiration_from_payload(self, drf_request, mocker):
        """Test revoking a token with expiration extracted from payload."""
        # Create a token with expiration
        exp_time = timezone.now() + timedelta(hours=2)
        payload = {
            "exp": int(exp_time.timestamp()),
            "sub": "test-subject",
            "email": "test@example.com",
        }

        # Use settings.SECRET_KEY as we don't need RSA for this test
        from django.conf import settings

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        # Mock jwt.decode to return our payload
        mocker.patch("oua_auth.authentication.jwt.decode", return_value=payload)

        # Revoke the token
        result = OUAJWTAuthentication.revoke_token(token)

        # Should succeed
        assert result is True

        # Check token in blacklist
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        blacklisted_token = BlacklistedToken.objects.get(token_hash=token_hash)

        # Expiration time should match token payload
        expected_expiry = exp_time.replace(microsecond=0)
        saved_expiry = blacklisted_token.expires_at.replace(microsecond=0)
        assert saved_expiry == expected_expiry


@pytest.fixture
def clear_blacklist():
    """Clear the token blacklist between tests."""
    _token_blacklist.clear()
    yield
    _token_blacklist.clear()


class TestTokenBlacklist:
    """Tests for token blacklist functions."""

    def test_add_token_to_memory_blacklist(self, clear_blacklist):
        """Test adding a token to memory blacklist."""
        # Create a token hash
        token_hash = "test-token-hash"

        # Add to blacklist
        result = add_token_to_memory_blacklist(token_hash)

        # Verify result is True
        assert result is True

        # Verify token is in blacklist
        assert token_hash in _token_blacklist

    @pytest.mark.django_db
    def test_is_token_in_memory_blacklist(self, clear_blacklist):
        """Test checking if a token is in memory blacklist."""
        # Create a token hash
        token_hash = "test-token-hash"

        # Initially token should not be in blacklist
        assert is_token_in_memory_blacklist(token_hash) is False

        # Add token to blacklist
        _token_blacklist.add(token_hash)

        # Now token should be in blacklist
        assert is_token_in_memory_blacklist(token_hash) is True

    @pytest.mark.django_db
    @patch("oua_auth.models.BlacklistedToken")
    def test_initialize_token_blacklist_success(self, mock_blacklisted_token):
        """Test successful initialization of token blacklist with database."""
        # Setup mock
        mock_blacklisted_token.clean_expired_tokens.return_value = 5

        # Call initialize
        result = initialize_token_blacklist()

        # Verify result is True
        assert result is True

        # Verify expired tokens were cleaned
        mock_blacklisted_token.clean_expired_tokens.assert_called_once()

    @pytest.mark.django_db
    @patch("oua_auth.models.BlacklistedToken")
    def test_initialize_token_blacklist_zero_expired(self, mock_blacklisted_token):
        """Test initialization when no expired tokens are found."""
        # Setup mock
        mock_blacklisted_token.clean_expired_tokens.return_value = 0

        # Call initialize
        result = initialize_token_blacklist()

        # Verify result is True
        assert result is True

        # Verify expired tokens were cleaned
        mock_blacklisted_token.clean_expired_tokens.assert_called_once()

    def test_initialize_token_blacklist_import_error(self):
        """Test initialization with import error."""
        with patch("oua_auth.token_blacklist.models", create=True) as mock_models:
            # Configure the mock to raise ImportError when accessed
            mock_models.__getattribute__ = MagicMock(
                side_effect=ImportError("Test import error")
            )

            # Call initialize
            result = initialize_token_blacklist()

            # Verify result is False due to error
            assert result is False

    @patch("oua_auth.models.BlacklistedToken")
    def test_initialize_token_blacklist_exception(self, mock_blacklisted_token):
        """Test initialization with other exception."""
        # Setup mock to raise exception
        mock_blacklisted_token.clean_expired_tokens.side_effect = ValueError(
            "Test error"
        )

        # Call initialize
        result = initialize_token_blacklist()

        # Verify result is False due to error
        assert result is False


class TestTokenBlacklistMemory:
    """Tests for memory-based token blacklist."""

    def test_blacklist_is_thread_safe(self):
        """Test that the blacklist lock provides thread safety."""
        from oua_auth.token_blacklist import _blacklist_lock

        # Verify lock exists
        assert _blacklist_lock is not None

        # Verify lock can be acquired
        acquired = _blacklist_lock.acquire(blocking=False)
        assert acquired is True

        # Release the lock
        _blacklist_lock.release()

    def test_memory_blacklist_multiple_tokens(self, clear_blacklist):
        """Test adding multiple tokens to memory blacklist."""
        # Add multiple tokens
        tokens = ["token1", "token2", "token3"]
        for token in tokens:
            add_token_to_memory_blacklist(token)

        # Verify all tokens are in blacklist
        for token in tokens:
            assert is_token_in_memory_blacklist(token) is True

        # Verify non-existent token is not in blacklist
        assert is_token_in_memory_blacklist("non-existent") is False

    def test_memory_blacklist_with_hashed_tokens(self, clear_blacklist):
        """Test memory blacklist with SHA-256 hashed tokens."""
        # Create tokens and their hashes
        tokens = ["raw-token1", "raw-token2"]
        token_hashes = [hashlib.sha256(token.encode()).hexdigest() for token in tokens]

        # Add token hashes to blacklist
        for token_hash in token_hashes:
            add_token_to_memory_blacklist(token_hash)

        # Verify token hashes are in blacklist
        for token_hash in token_hashes:
            assert is_token_in_memory_blacklist(token_hash) is True
