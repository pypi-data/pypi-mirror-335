"""Authentication backend for OrganizationUnifiedAccess (OUA)."""

import logging
import requests
from django.contrib.auth import get_user_model
from django.conf import settings
import bleach
import re
from oua_auth.authentication import OUAJWTAuthentication
from oua_auth.logging_utils import setup_logging


# Set up logger
logger = setup_logging(__name__)


class OUAAuthBackend:
    """
    Authentication backend for the OrganizationUnifiedAccess (OUA) SSO system.

    This backend authenticates users by validating JWT tokens from the OUA SSO server.
    It creates or updates Django users based on the claims in the token.
    """

    def __init__(self):
        """Initialize the authentication backend with required settings."""
        # Get SSO URL from settings
        self.sso_url = getattr(settings, "OUA_SSO_URL", "https://test-sso.example.com")

        # Set up a requests session for better performance with keep-alive
        self.session = requests.Session()

        # Request timeout for API calls to SSO server
        self.request_timeout = getattr(settings, "OUA_VERIFY_TIMEOUT", 5)

        # Admin privilege controls
        self.trusted_admin_domains = getattr(settings, "OUA_TRUSTED_ADMIN_DOMAINS", [])
        self.trusted_admin_emails = getattr(settings, "OUA_TRUSTED_ADMIN_EMAILS", [])

        # Max length for sanitized inputs
        self.max_field_length = getattr(settings, "OUA_MAX_FIELD_LENGTH", 100)

    def authenticate(self, request, token=None, **kwargs):
        """
        Authenticate a user based on a JWT token.

        Args:
            request: The HTTP request object
            token: The JWT token to validate

        Returns:
            User object if authentication succeeds, None otherwise
        """
        if token is None:
            return None

        # Create instance-specific logger with context
        log = logger.with_context(
            component="auth_backend",
            request_id=getattr(request, "id", None),
        )

        try:
            # Use the OUA JWT authentication class to validate the token
            auth = OUAJWTAuthentication()

            # Add the token to the request for authentication
            request.META["HTTP_AUTHORIZATION"] = f"Bearer {token}"

            # Authenticate using the token
            user_and_token = auth.authenticate(request)

            if user_and_token is not None:
                user, internal_token = user_and_token
                log.info(
                    "Successfully authenticated user with token",
                    extra={"user_id": user.id, "email": user.email},
                )

                # Store the internal token in the request for use in views
                request.internal_token = internal_token

                return user

            log.warning("Token authentication failed")
            return None

        except Exception as e:
            log.error(
                f"Authentication error: {str(e)}",
                extra={"error_class": type(e).__name__},
                exc_info=True,
            )
            return None

    def get_user(self, user_id):
        """
        Retrieve a user by ID.

        Args:
            user_id: The ID of the user to retrieve

        Returns:
            User object if found, None otherwise
        """
        User = get_user_model()

        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def _sanitize_input(self, input_value):
        """
        Sanitize input to prevent XSS and injection attacks.

        Args:
            input_value: The value to sanitize

        Returns:
            Sanitized value
        """
        # Return non-string values as-is (except None)
        if input_value is None:
            return ""

        if not isinstance(input_value, str):
            return input_value

        # Clean the string using bleach to remove any potentially harmful HTML
        # Setting tags=[] ensures all HTML tags are removed
        cleaned = bleach.clean(input_value, tags=[], strip=True)

        # Normalize whitespace (replace multiple spaces, newlines, tabs with a single space)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        # Truncate if needed
        if len(cleaned) > self.max_field_length:
            cleaned = cleaned[: self.max_field_length]

        return cleaned

    def _validate_email_format(self, email):
        """
        Validate email format.

        Args:
            email: The email address to validate

        Returns:
            True if valid, False otherwise
        """
        # Basic email format validation
        email_pattern = r"^[\w.+-]+@[\w-]+\.[\w.-]+$"
        return bool(re.match(email_pattern, email))

    def _is_trusted_admin(self, email):
        """
        Check if the email belongs to a trusted admin.

        Args:
            email: The email address to check

        Returns:
            True if trusted admin, False otherwise
        """
        # For backward compatibility, if both lists are empty, trust all admins
        if not self.trusted_admin_domains and not self.trusted_admin_emails:
            return True

        # Check exact email match
        if email in self.trusted_admin_emails:
            return True

        # Check domain match
        domain = email.split("@")[-1]
        return domain in self.trusted_admin_domains
