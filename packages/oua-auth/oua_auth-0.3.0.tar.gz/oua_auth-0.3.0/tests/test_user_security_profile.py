"""Tests for the user security profile functionality."""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, UTC
from django.utils import timezone

from oua_auth.models import UserSecurityProfile


@pytest.mark.django_db
class TestUserSecurityProfile:
    """Tests for the UserSecurityProfile class and methods."""

    def test_user_security_profile_create(self, user_regular):
        """Test UserSecurityProfile creation."""
        profile = UserSecurityProfile.objects.create(user=user_regular)

        # Verify initial values
        assert profile.user.id == user_regular.id
        assert profile.is_locked is False
        assert profile.lock_reason is None
        assert profile.locked_until is None
        assert profile.failed_login_attempts == 0
        assert profile.last_failed_login is None

    def test_lock_account(self, user_regular):
        """Test locking a user account."""
        profile = UserSecurityProfile.objects.create(user=user_regular)

        # Lock the account
        reason = "Security violation"
        result = profile.lock_account(reason, duration_hours=2)

        # Verify result and account state
        assert result is True
        assert profile.is_locked is True
        assert profile.lock_reason == reason

        # Verify locked_until is approximately 2 hours in the future
        locked_duration = profile.locked_until - timezone.now()
        assert locked_duration.total_seconds() > 7100  # Just under 2 hours
        assert locked_duration.total_seconds() < 7300  # Just over 2 hours

    def test_unlock_account(self, user_regular):
        """Test unlocking a user account."""
        profile = UserSecurityProfile.objects.create(
            user=user_regular,
            is_locked=True,
            lock_reason="Test lock",
            locked_until=timezone.now() + timedelta(hours=1),
            failed_login_attempts=5,
        )

        # Unlock the account
        result = profile.unlock_account()

        # Verify result and account state
        assert result is True
        assert profile.is_locked is False
        assert profile.lock_reason is None
        assert profile.locked_until is None
        assert profile.failed_login_attempts == 0

    def test_record_failed_login(self, user_regular):
        """Test recording a failed login."""
        profile = UserSecurityProfile.objects.create(user=user_regular)

        # Record a failed login
        before_time = timezone.now()
        result = profile.record_failed_login(ip_address="192.168.1.1")
        after_time = timezone.now()

        # Verify result and account state
        assert result == 1  # First failure
        assert profile.failed_login_attempts == 1
        assert profile.last_login_ip == "192.168.1.1"
        assert before_time <= profile.last_failed_login <= after_time

        # Record another failed login without IP
        result = profile.record_failed_login()

        # Verify result and account state
        assert result == 2  # Second failure
        assert profile.failed_login_attempts == 2
        assert profile.last_login_ip == "192.168.1.1"  # Unchanged

    def test_record_successful_login(self, user_regular):
        """Test recording a successful login."""
        profile = UserSecurityProfile.objects.create(
            user=user_regular, failed_login_attempts=3
        )

        # Record a successful login
        result = profile.record_successful_login(ip_address="10.0.0.1")

        # Verify result and account state
        assert result is True
        assert profile.failed_login_attempts == 0  # Reset to zero
        assert profile.last_login_ip == "10.0.0.1"

    def test_auto_create_profiles(self, user_regular, user_admin):
        """Test auto_create_profiles class method."""
        # Ensure no profiles exist initially
        UserSecurityProfile.objects.all().delete()

        # Call auto_create_profiles
        count = UserSecurityProfile.auto_create_profiles()

        # Verify profiles were created
        assert count >= 2  # At least for our 2 test users

        # Verify both test users have profiles
        assert UserSecurityProfile.objects.filter(user=user_regular).exists()
        assert UserSecurityProfile.objects.filter(user=user_admin).exists()

        # Calling again should create no new profiles
        count = UserSecurityProfile.auto_create_profiles()
        assert count == 0
