"""Management command to clean expired tokens from the blacklist."""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import datetime, UTC
from oua_auth.models import BlacklistedToken


class Command(BaseCommand):
    """Command to clean expired tokens from the blacklist."""

    help = "Cleans expired blacklisted tokens from the database"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without actually deleting",
        )

    def handle(self, *args, **options):
        """Handle the command execution."""
        dry_run = options.get("dry_run", False)

        # Get current time for comparison
        now = datetime.now(UTC)

        # Query for expired tokens
        expired_tokens = BlacklistedToken.objects.filter(expires_at__lt=now)
        count = expired_tokens.count()

        if dry_run:
            self.stdout.write(f"Would delete {count} expired tokens (dry run)")
        else:
            # Delete the expired tokens
            result = expired_tokens.delete()
            self.stdout.write(
                self.style.SUCCESS(f"Successfully deleted {count} expired tokens")
            )

        return count
