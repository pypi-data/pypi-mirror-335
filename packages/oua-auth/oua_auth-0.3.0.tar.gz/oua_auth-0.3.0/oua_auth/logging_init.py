"""
Logging initialization for OUA Auth.

This module initializes logging configuration for the OUA Auth package.
It can be imported early in the application lifecycle to ensure proper
logging setup before other modules are loaded.
"""

import logging
from django.apps import AppConfig
from django.conf import settings


class OUALoggingAppConfig(AppConfig):
    """
    Application configuration for OUA Auth logging.

    This ensures proper logging setup when Django initializes.
    """

    name = "oua_auth.logging"
    verbose_name = "OUA Auth Logging"

    def ready(self):
        """Initialize logging when Django is ready."""
        initialize_logging()


def initialize_logging():
    """
    Initialize logging configuration for OUA Auth.

    This function configures structured logging with sensitive data filtering.
    It can be called explicitly or will be called automatically through
    the Django AppConfig.
    """
    try:
        # Check if eager logging is enabled in settings
        eager_logging = getattr(settings, "OUA_EAGER_LOGGING", False)

        if eager_logging:
            # Import and configure logging
            from .logging_utils import configure_oua_logging

            configure_oua_logging()

            logger = logging.getLogger(__name__)
            logger.debug("OUA Auth logging initialized early")
    except (ImportError, ModuleNotFoundError):
        # Django might not be fully initialized yet
        logging.basicConfig(level=logging.INFO)
        logging.warning("OUA Auth early logging initialization skipped")
    except Exception as e:
        # Log any unexpected errors during initialization
        logging.basicConfig(level=logging.INFO)
        logging.error(f"Error initializing OUA Auth logging: {str(e)}")

    # Register signal handlers or perform other initialization as needed
