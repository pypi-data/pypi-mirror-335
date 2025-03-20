"""Tests for logging initialization."""

import pytest
from unittest.mock import patch, MagicMock
import logging
import os
import sys

from oua_auth.logging_init import initialize_logging, OUALoggingAppConfig


class TestLoggingInit:
    """Tests for logging initialization."""

    @patch("oua_auth.logging_init.settings")
    @patch("oua_auth.logging_init.logging")
    def test_initialize_logging_eager_disabled(self, mock_logging, mock_settings):
        """Test initialize_logging when eager logging is disabled."""
        # Configure settings mock
        mock_settings.OUA_EAGER_LOGGING = False

        # Call the function
        initialize_logging()

        # Verify no logging configuration was attempted
        mock_logging.basicConfig.assert_not_called()

    @patch("oua_auth.logging_init.settings")
    @patch("oua_auth.logging_init.logging")
    def test_initialize_logging_eager_enabled(self, mock_logging, mock_settings):
        """Test initialize_logging when eager logging is enabled."""
        # Configure settings mock
        mock_settings.OUA_EAGER_LOGGING = True

        # Mock the imported function
        with patch("oua_auth.logging_utils.configure_oua_logging") as mock_configure:
            # Call the function
            initialize_logging()

            # Verify logging was configured
            mock_configure.assert_called_once()

    @patch("oua_auth.logging_init.settings")
    @patch("oua_auth.logging_init.logging")
    def test_initialize_logging_import_error(self, mock_logging, mock_settings):
        """Test initialize_logging when an import error occurs."""
        # Configure settings mock
        mock_settings.OUA_EAGER_LOGGING = True

        # Mock the import statement to raise an ImportError
        with patch.dict("sys.modules", {"oua_auth.logging_utils": None}):
            # Force import to raise ImportError when trying to access the module
            with patch(
                "builtins.__import__", side_effect=ImportError("Test import error")
            ):
                # Call the function
                initialize_logging()

                # Verify basic logging was configured and warning was logged
                mock_logging.basicConfig.assert_called_once()
                mock_logging.warning.assert_called_once()
                assert (
                    "early logging initialization skipped"
                    in mock_logging.warning.call_args[0][0]
                )

    @patch("oua_auth.logging_init.settings")
    @patch("oua_auth.logging_init.logging")
    def test_initialize_logging_general_exception(self, mock_logging, mock_settings):
        """Test initialize_logging when a general exception occurs."""
        # Configure settings mock
        mock_settings.OUA_EAGER_LOGGING = True

        # Force a general exception
        with patch(
            "oua_auth.logging_utils.configure_oua_logging",
            side_effect=Exception("Test error"),
        ):
            # Call the function
            initialize_logging()

            # Verify basic logging was set up and error was logged
            mock_logging.basicConfig.assert_called_once()
            mock_logging.error.assert_called_once()
            assert "Error initializing" in mock_logging.error.call_args[0][0]

    def test_app_config_properties(self):
        """Test OUALoggingAppConfig properties."""
        # Create a mock module with __file__ attribute for path detection
        mock_module = MagicMock()
        mock_module.__file__ = os.path.join(os.path.dirname(__file__), "__init__.py")

        config = OUALoggingAppConfig(
            app_name="oua_auth.logging", app_module=mock_module
        )

        assert config.name == "oua_auth.logging"
        assert config.verbose_name == "OUA Auth Logging"

    @patch("oua_auth.logging_init.initialize_logging")
    def test_app_config_ready(self, mock_initialize):
        """Test OUALoggingAppConfig.ready method."""
        # Create a mock module with __file__ attribute for path detection
        mock_module = MagicMock()
        mock_module.__file__ = os.path.join(os.path.dirname(__file__), "__init__.py")

        config = OUALoggingAppConfig(
            app_name="oua_auth.logging", app_module=mock_module
        )

        # Call the ready method
        config.ready()

        # Verify initialize_logging was called
        mock_initialize.assert_called_once()
