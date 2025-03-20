"""
Django application configuration for OUA Auth.
"""

from django.apps import AppConfig
import logging
from django.db.models.signals import post_migrate

logger = logging.getLogger(__name__)


def perform_post_migration_tasks(sender, **kwargs):
    """
    Perform tasks that require database access after migrations complete.

    This function is connected to the post_migrate signal to ensure
    database operations happen only after the database is fully set up.
    """
    # Initialize token blacklist
    try:
        from .token_blacklist import initialize_token_blacklist

        initialize_token_blacklist()
        logger.info("Token blacklist initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize token blacklist: {e}")

    # Auto-create security profiles for users without them
    try:
        from .models import UserSecurityProfile

        if hasattr(UserSecurityProfile, "auto_create_profiles"):
            count = UserSecurityProfile.auto_create_profiles()
            if count > 0:
                logger.info(f"Created {count} missing user security profiles")
    except Exception as e:
        logger.warning(f"Failed to create user security profiles: {e}")


class OUAAppConfig(AppConfig):
    """
    OUA Auth application configuration.

    This configures the OUA authentication app and initializes
    logging and other required services.
    """

    name = "oua_auth"
    verbose_name = "Organization Unified Access Authentication"

    def ready(self):
        """
        Initialize the application when Django is ready.

        This method is called when the Django application registry is fully populated.
        """
        # Initialize logging (this doesn't require database access)
        from .logging_init import initialize_logging

        initialize_logging()

        # Connect the post_migrate signal handler for database operations
        # This ensures database operations happen only after migrations
        post_migrate.connect(perform_post_migration_tasks, sender=self)

        logger.info("OUA Auth application initialized")
