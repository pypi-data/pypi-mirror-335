"""
Token blacklist initialization and management for OUA Auth.

This module provides functionality for initializing and managing
the token blacklist system used to revoke access tokens.
"""

import logging
import threading

# In-memory token blacklist as fallback when database is not available
_token_blacklist = set()
_blacklist_lock = threading.RLock()  # Thread-safe operations on the blacklist

logger = logging.getLogger(__name__)


def initialize_token_blacklist():
    """
    Initialize the token blacklist system.

    This function is called during package initialization to set up
    the token blacklist system. It ensures proper database connectivity
    or falls back to in-memory implementation when needed.
    """
    try:
        # Try to import models to check if database is available
        from .models import BlacklistedToken

        # Clean up expired tokens on startup
        count = BlacklistedToken.clean_expired_tokens()
        if count > 0:
            logger.info(f"Removed {count} expired tokens from blacklist on startup")

        logger.debug("Token blacklist initialized using database storage")
        return True
    except (ImportError, ModuleNotFoundError):
        # Database not available, use in-memory fallback
        logger.warning(
            "Database not available for token blacklist, using in-memory fallback"
        )
        return False
    except Exception as e:
        # Log any unexpected errors during initialization
        logger.error(f"Error initializing token blacklist: {str(e)}")
        return False


def add_token_to_memory_blacklist(token_hash):
    """
    Add a token hash to the in-memory blacklist.

    This is used as a fallback when the database is not available.

    Args:
        token_hash: The SHA-256 hash of the token to blacklist
    """
    with _blacklist_lock:
        _token_blacklist.add(token_hash)

    logger.debug("Token added to in-memory blacklist")
    return True


def is_token_in_memory_blacklist(token_hash):
    """
    Check if a token hash is in the in-memory blacklist.

    This is used as a fallback when the database is not available.

    Args:
        token_hash: The SHA-256 hash of the token to check

    Returns:
        bool: True if the token is blacklisted, False otherwise
    """
    with _blacklist_lock:
        return token_hash in _token_blacklist
