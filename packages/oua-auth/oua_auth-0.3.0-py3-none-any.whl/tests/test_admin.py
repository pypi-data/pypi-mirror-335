"""Tests for admin functionality."""

import pytest
from django.urls import reverse
from django.test import RequestFactory, Client
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.utils import timezone
from datetime import timedelta, datetime, UTC

from oua_auth.admin import (
    BlacklistedTokenAdmin,
    SuspiciousActivityAdmin,
    UserSecurityProfileAdmin,
)
from oua_auth.models import BlacklistedToken, SuspiciousActivity, UserSecurityProfile


@pytest.fixture
def admin_site():
    """Create an admin site for testing."""
    return AdminSite()


@pytest.fixture
def admin_user(db):
    """Create an admin user for testing."""
    User = get_user_model()
    admin_user = User.objects.create_superuser(
        username="admin", email="admin@example.com", password="password"
    )
    return admin_user


@pytest.fixture
def logged_in_admin_client(admin_user):
    """Create a client with admin user logged in."""
    client = Client()
    client.login(username="admin", email="admin@example.com", password="password")
    return client


@pytest.fixture
def request_factory():
    """Create a request factory for testing."""
    return RequestFactory()


@pytest.fixture
def blacklisted_token_admin(admin_site):
    """Create a BlacklistedTokenAdmin instance for testing."""
    return BlacklistedTokenAdmin(BlacklistedToken, admin_site)


@pytest.fixture
def suspicious_activity_admin(admin_site):
    """Create a SuspiciousActivityAdmin instance for testing."""
    return SuspiciousActivityAdmin(SuspiciousActivity, admin_site)


@pytest.fixture
def user_security_profile_admin(admin_site):
    """Create a UserSecurityProfileAdmin instance for testing."""
    return UserSecurityProfileAdmin(UserSecurityProfile, admin_site)


def add_message_middleware(request):
    """Add message middleware to request for admin actions."""
    setattr(request, "session", "session")
    messages = FallbackStorage(request)
    setattr(request, "_messages", messages)
    return request


@pytest.mark.django_db
class TestBlacklistedTokenAdmin:
    """Tests for BlacklistedTokenAdmin."""

    def test_token_hash_truncated(self, blacklisted_token_admin):
        """Test the token_hash_truncated method."""
        token = BlacklistedToken(token_hash="0123456789abcdef0123456789abcdef")
        truncated = blacklisted_token_admin.token_hash_truncated(token)

        # Should display first 10 chars followed by "..."
        assert truncated == "0123456789..."

    def test_is_expired_with_expired_token(self, blacklisted_token_admin):
        """Test the is_expired method with an expired token."""
        expired_time = datetime.now(UTC) - timedelta(days=1)
        token = BlacklistedToken(expires_at=expired_time)

        result = blacklisted_token_admin.is_expired(token)

        # Should contain "Expired" text and "red" color
        assert "Expired" in result
        assert "red" in result

    def test_is_expired_with_active_token(self, blacklisted_token_admin):
        """Test the is_expired method with an active token."""
        active_time = datetime.now(UTC) + timedelta(days=1)
        token = BlacklistedToken(expires_at=active_time)

        result = blacklisted_token_admin.is_expired(token)

        # Should contain "Active" text and "green" color
        assert "Active" in result
        assert "green" in result

    def test_has_add_permission(self, request_factory, blacklisted_token_admin):
        """Test that the has_add_permission method returns False."""
        request = request_factory.get("/")

        # Should return False to prevent direct token creation
        assert blacklisted_token_admin.has_add_permission(request) is False

    def test_delete_expired_tokens_action(
        self, request_factory, blacklisted_token_admin
    ):
        """Test the delete_expired_tokens action."""
        # Create expired tokens
        expired_time = datetime.now(UTC) - timedelta(days=1)
        BlacklistedToken.objects.create(
            token_hash="expired1",
            blacklisted_by="test@example.com",
            reason="Test",
            expires_at=expired_time,
        )
        BlacklistedToken.objects.create(
            token_hash="expired2",
            blacklisted_by="test@example.com",
            reason="Test",
            expires_at=expired_time,
        )

        # Create request
        request = request_factory.post("/")
        request = add_message_middleware(request)

        # Create queryset (not used by the action, but required as parameter)
        queryset = BlacklistedToken.objects.all()

        # Call the action
        blacklisted_token_admin.delete_expired_tokens(request, queryset)

        # Verify that expired tokens were deleted
        assert BlacklistedToken.objects.count() == 0

    def test_extend_expiration_action(self, request_factory, blacklisted_token_admin):
        """Test the extend_expiration action."""
        # Create token
        token_time = datetime.now(UTC)
        token = BlacklistedToken.objects.create(
            token_hash="token1",
            blacklisted_by="test@example.com",
            reason="Test",
            expires_at=token_time,
        )

        # Create request
        request = request_factory.post("/")
        request = add_message_middleware(request)

        # Create queryset with the token
        queryset = BlacklistedToken.objects.all()

        # Call the action
        blacklisted_token_admin.extend_expiration(request, queryset)

        # Refresh token from database
        token.refresh_from_db()

        # Expiration should be extended by one day (within a small margin of error)
        expected_time = token_time + timedelta(days=1)
        time_difference = abs((token.expires_at - expected_time).total_seconds())

        # Allow a small margin (1 second) for timing variations during test execution
        assert time_difference < 1


@pytest.mark.django_db
class TestSuspiciousActivityAdmin:
    """Tests for SuspiciousActivityAdmin."""

    def test_details_truncated_with_long_text(self, suspicious_activity_admin):
        """Test the details_truncated method with long details text."""
        activity = SuspiciousActivity(details="A" * 100)

        truncated = suspicious_activity_admin.details_truncated(activity)

        # Should truncate to 47 chars + "..."
        assert len(truncated) == 50
        assert truncated.endswith("...")

    def test_details_truncated_with_short_text(self, suspicious_activity_admin):
        """Test the details_truncated method with short details text."""
        activity = SuspiciousActivity(details="Short text")

        truncated = suspicious_activity_admin.details_truncated(activity)

        # Should return the original text
        assert truncated == "Short text"

    def test_details_truncated_with_none(self, suspicious_activity_admin):
        """Test the details_truncated method with None details."""
        activity = SuspiciousActivity(details=None)

        truncated = suspicious_activity_admin.details_truncated(activity)

        # Should return a placeholder
        assert truncated == "—"

    def test_cleanup_old_activities_action(
        self, request_factory, suspicious_activity_admin
    ):
        """Test the cleanup_old_activities action."""
        # Create old activity (35 days ago)
        old_time = timezone.now() - timedelta(days=35)
        SuspiciousActivity.objects.create(
            user_identifier="old_user",
            activity_type="login_failed",
            ip_address="127.0.0.1",
            timestamp=old_time,
            details="Old activity",
        )

        # Create recent activity (25 days ago)
        recent_time = timezone.now() - timedelta(days=25)
        SuspiciousActivity.objects.create(
            user_identifier="recent_user",
            activity_type="login_failed",
            ip_address="127.0.0.1",
            timestamp=recent_time,
            details="Recent activity",
        )

        # Create request
        request = request_factory.post("/")
        request = add_message_middleware(request)

        # Create queryset (not used by the action, but required as parameter)
        queryset = SuspiciousActivity.objects.all()

        # Call the action with default days=30
        suspicious_activity_admin.cleanup_old_activities(request, queryset)

        # Verify that only old activity was deleted
        assert SuspiciousActivity.objects.count() == 1
        assert SuspiciousActivity.objects.filter(user_identifier="recent_user").exists()
        assert not SuspiciousActivity.objects.filter(
            user_identifier="old_user"
        ).exists()


@pytest.mark.django_db
class TestUserSecurityProfileAdmin:
    """Tests for UserSecurityProfileAdmin."""

    def test_user_email_method(self, user_security_profile_admin):
        """Test the user_email method."""
        User = get_user_model()
        user = User.objects.create(username="testuser", email="user@example.com")
        profile = UserSecurityProfile(user=user)

        email = user_security_profile_admin.user_email(profile)

        assert email == "user@example.com"

    def test_unlock_accounts_action(self, request_factory, user_security_profile_admin):
        """Test the unlock_accounts action."""
        # Create users
        User = get_user_model()
        user1 = User.objects.create(username="user1", email="user1@example.com")
        user2 = User.objects.create(username="user2", email="user2@example.com")

        # Create locked profiles
        profile1 = UserSecurityProfile.objects.create(
            user=user1,
            is_locked=True,
            locked_until=timezone.now() + timedelta(hours=1),
            lock_reason="Too many failed attempts",
        )
        profile2 = UserSecurityProfile.objects.create(
            user=user2,
            is_locked=True,
            locked_until=timezone.now() + timedelta(hours=1),
            lock_reason="Too many failed attempts",
        )

        # Create request
        request = request_factory.post("/")
        request = add_message_middleware(request)

        # Create queryset with the profiles
        queryset = UserSecurityProfile.objects.all()

        # Call the action
        user_security_profile_admin.unlock_accounts(request, queryset)

        # Refresh profiles from database
        profile1.refresh_from_db()
        profile2.refresh_from_db()

        # Verify that profiles were unlocked
        assert profile1.is_locked is False
        assert profile2.is_locked is False
        assert profile1.locked_until is None
        assert profile2.locked_until is None

    def test_reset_failed_attempts_action(
        self, request_factory, user_security_profile_admin
    ):
        """Test the reset_failed_attempts action."""
        # Create users
        User = get_user_model()
        user1 = User.objects.create(username="user1", email="user1@example.com")
        user2 = User.objects.create(username="user2", email="user2@example.com")

        # Create profiles with failed attempts
        profile1 = UserSecurityProfile.objects.create(
            user=user1, failed_login_attempts=3
        )
        profile2 = UserSecurityProfile.objects.create(
            user=user2, failed_login_attempts=5
        )

        # Create request
        request = request_factory.post("/")
        request = add_message_middleware(request)

        # Create queryset with the profiles
        queryset = UserSecurityProfile.objects.all()

        # Call the action
        user_security_profile_admin.reset_failed_attempts(request, queryset)

        # Refresh profiles from database
        profile1.refresh_from_db()
        profile2.refresh_from_db()

        # Verify that failed attempts were reset
        assert profile1.failed_login_attempts == 0
        assert profile2.failed_login_attempts == 0
