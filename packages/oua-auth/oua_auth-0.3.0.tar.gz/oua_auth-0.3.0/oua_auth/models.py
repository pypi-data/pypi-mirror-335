"""Database models for the OUA SSO authentication package."""

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
import hashlib
import logging

logger = logging.getLogger(__name__)


class BlacklistedToken(models.Model):
    """Model to store blacklisted JWT tokens.

    Stores a hash of the token rather than the token itself for security reasons.
    Includes expiration time to allow for automatic cleanup of expired tokens.
    """

    token_hash = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    blacklisted_by = models.CharField(max_length=255, blank=True, null=True)
    reason = models.TextField(blank=True, null=True)

    class Meta:
        """Meta options for the BlacklistedToken model."""

        verbose_name = "Blacklisted Token"
        verbose_name_plural = "Blacklisted Tokens"
        indexes = [
            models.Index(fields=["expires_at"]),
        ]

    @classmethod
    def add_token_to_blacklist(
        cls, token, expires_at=None, blacklisted_by=None, reason=None
    ):
        """Add a token to the blacklist.

        Args:
            token: The JWT token to blacklist
            expires_at: When the token expires (derived from token if not provided)
            blacklisted_by: Optional identifier of who blacklisted the token
            reason: Optional reason for blacklisting

        Returns:
            The created BlacklistedToken instance
        """
        # Create a SHA-256 hash of the token for secure storage
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # Use provided expiration or default to 24 hours from now
        if expires_at is None:
            expires_at = timezone.now() + timezone.timedelta(hours=24)

        # Create the blacklist entry, using get_or_create to handle potential race conditions
        blacklisted_token, created = cls.objects.update_or_create(
            token_hash=token_hash,
            defaults={
                "expires_at": expires_at,
                "blacklisted_by": blacklisted_by,
                "reason": reason,
            },
        )

        return blacklisted_token

    @classmethod
    def is_token_blacklisted(cls, token):
        """Check if a token is blacklisted.

        Args:
            token: The JWT token to check

        Returns:
            bool: True if token is blacklisted, False otherwise
        """
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # Clean up expired tokens first to keep the table size manageable
        cls.clean_expired_tokens()

        # Check if token exists in blacklist
        return cls.objects.filter(token_hash=token_hash).exists()

    @classmethod
    def clean_expired_tokens(cls):
        """Remove expired tokens from the blacklist."""
        deleted, _ = cls.objects.filter(expires_at__lt=timezone.now()).delete()
        return deleted

    def __str__(self):
        return f"Blacklisted token (expires: {self.expires_at})"


class SuspiciousActivity(models.Model):
    """
    Model for tracking suspicious authentication activities.

    Used for automatic account locking after suspicious behavior.
    """

    # Use a generic identifier instead of a foreign key to allow tracking
    # activities for users that don't exist yet or anonymous attempts
    user_identifier = models.CharField(max_length=255, db_index=True)
    ip_address = models.CharField(max_length=45, blank=True, null=True, db_index=True)
    activity_type = models.CharField(max_length=50, db_index=True)
    details = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        verbose_name = "Suspicious Activity"
        verbose_name_plural = "Suspicious Activities"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user_identifier", "timestamp"]),
            models.Index(fields=["ip_address", "timestamp"]),
        ]

    @classmethod
    def cleanup_old_activities(cls, days=30):
        """Remove activities older than specified days."""
        cutoff = timezone.now() - timezone.timedelta(days=days)
        deleted, _ = cls.objects.filter(timestamp__lt=cutoff).delete()
        return deleted

    def __str__(self):
        return f"{self.activity_type} by {self.user_identifier} at {self.timestamp}"


# Add a UserProfile model with locking fields if the default User model doesn't have them
try:
    # Check if User model has necessary fields
    User = get_user_model()
    has_lock_fields = hasattr(User, "is_locked") and hasattr(User, "lock_reason")

    if not has_lock_fields:

        class UserSecurityProfile(models.Model):
            """
            Extended security profile for users with account locking functionality.
            """

            user = models.OneToOneField(
                User, on_delete=models.CASCADE, related_name="security_profile"
            )
            is_locked = models.BooleanField(default=False)
            lock_reason = models.CharField(max_length=255, blank=True, null=True)
            locked_until = models.DateTimeField(blank=True, null=True)
            failed_login_attempts = models.PositiveIntegerField(default=0)
            last_failed_login = models.DateTimeField(blank=True, null=True)
            last_login_ip = models.CharField(max_length=45, blank=True, null=True)

            class Meta:
                verbose_name = "User Security Profile"
                verbose_name_plural = "User Security Profiles"

            def lock_account(self, reason, duration_hours=24):
                """Lock the user account for the specified duration."""
                self.is_locked = True
                self.lock_reason = reason
                self.locked_until = timezone.now() + timezone.timedelta(
                    hours=duration_hours
                )
                self.save(update_fields=["is_locked", "lock_reason", "locked_until"])
                return True

            def unlock_account(self):
                """Unlock the user account."""
                self.is_locked = False
                self.lock_reason = None
                self.locked_until = None
                self.failed_login_attempts = 0
                self.save(
                    update_fields=[
                        "is_locked",
                        "lock_reason",
                        "locked_until",
                        "failed_login_attempts",
                    ]
                )
                return True

            def record_failed_login(self, ip_address=None):
                """Record a failed login attempt."""
                self.failed_login_attempts += 1
                self.last_failed_login = timezone.now()
                if ip_address:
                    self.last_login_ip = ip_address
                self.save(
                    update_fields=[
                        "failed_login_attempts",
                        "last_failed_login",
                        "last_login_ip",
                    ]
                )
                return self.failed_login_attempts

            def record_successful_login(self, ip_address=None):
                """Record a successful login, resetting the failed count."""
                self.failed_login_attempts = 0
                if ip_address:
                    self.last_login_ip = ip_address
                self.save(update_fields=["failed_login_attempts", "last_login_ip"])
                return True

            def __str__(self):
                status = "LOCKED" if self.is_locked else "active"
                return f"Security Profile for {self.user.email} ({status})"

            @classmethod
            def auto_create_profiles(cls):
                """
                Create security profiles for all users that don't have one.

                Returns:
                    int: Number of profiles created
                """
                users_without_profiles = User.objects.filter(
                    security_profile__isnull=True
                )
                count = 0

                for user in users_without_profiles:
                    cls.objects.create(user=user)
                    count += 1

                return count

except Exception as e:
    # Silently continue if we can't add the model
    # This might happen during initial migrations
    pass
