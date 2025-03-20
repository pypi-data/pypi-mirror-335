"""Tests for the clean_expired_tokens management command."""

import pytest
from unittest.mock import patch, MagicMock, ANY
from django.core.management import call_command
from io import StringIO
from datetime import timedelta
from django.utils import timezone

from oua_auth.models import BlacklistedToken
from oua_auth.management.commands.clean_expired_tokens import Command


@pytest.mark.django_db
class TestCleanExpiredTokensCommand:
    """Tests for the clean_expired_tokens management command."""

    def setup_method(self):
        """Clear all blacklisted tokens before each test."""
        BlacklistedToken.objects.all().delete()

    def test_command_dry_run(self):
        """Test that the command in dry run mode displays the correct count without deleting."""
        # Create expired tokens
        expired_time = timezone.now() - timedelta(days=1)
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

        # Create active token
        active_time = timezone.now() + timedelta(days=1)
        BlacklistedToken.objects.create(
            token_hash="active1",
            blacklisted_by="test@example.com",
            reason="Test",
            expires_at=active_time,
        )

        # Verify initial count
        assert BlacklistedToken.objects.count() == 3
        assert (
            BlacklistedToken.objects.filter(expires_at__lt=timezone.now()).count() == 2
        )

        # Directly call the command's handle method to test dry_run mode
        cmd = Command()
        # Create a mock stdout to capture output
        cmd.stdout = MagicMock()

        # Execute command in dry-run mode
        cmd.handle(dry_run=True)

        # Check that the mock was called with the expected message
        cmd.stdout.write.assert_any_call(f"Would delete 2 expired tokens (dry run)")

        # Verify tokens weren't deleted in dry-run mode
        assert BlacklistedToken.objects.count() == 3

    def test_command_actual_deletion(self):
        """Test that the command actually deletes expired tokens."""
        # Create expired tokens
        expired_time = timezone.now() - timedelta(days=1)
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

        # Create active token
        active_time = timezone.now() + timedelta(days=1)
        BlacklistedToken.objects.create(
            token_hash="active1",
            blacklisted_by="test@example.com",
            reason="Test",
            expires_at=active_time,
        )

        # Verify initial count
        assert BlacklistedToken.objects.count() == 3

        # Execute command directly rather than through call_command
        cmd = Command()
        cmd.handle(dry_run=False)

        # Verify only expired tokens were deleted
        assert BlacklistedToken.objects.count() == 1
        assert BlacklistedToken.objects.filter(token_hash="active1").exists()
        assert not BlacklistedToken.objects.filter(token_hash="expired1").exists()
        assert not BlacklistedToken.objects.filter(token_hash="expired2").exists()

    def test_command_no_expired_tokens(self):
        """Test that the command handles the case when there are no expired tokens."""
        # Create only active tokens
        active_time = timezone.now() + timedelta(days=1)
        BlacklistedToken.objects.create(
            token_hash="active1",
            blacklisted_by="test@example.com",
            reason="Test",
            expires_at=active_time,
        )

        # Verify initial count
        assert BlacklistedToken.objects.count() == 1

        # Execute command directly
        cmd = Command()
        result = cmd.handle(dry_run=False)

        # Check the result
        assert result == 0

        # Verify no tokens were deleted
        assert BlacklistedToken.objects.count() == 1
