"""Tests for the application configuration."""

import pytest
from unittest.mock import patch, MagicMock, PropertyMock

from oua_auth.apps import OUAAppConfig, perform_post_migration_tasks


@pytest.fixture
def mock_app_config():
    """Create a properly mocked AppConfig instance."""
    config = MagicMock(spec=OUAAppConfig)
    config.name = "oua_auth"
    config.verbose_name = "Organization Unified Access Authentication"
    return config


class TestOUAAppConfig:
    """Tests for the OUA Auth application configuration."""

    def test_app_name(self):
        """Test the app name is correctly set."""
        config = OUAAppConfig.__new__(OUAAppConfig)
        config.name = "oua_auth"
        config.path = "/test/path"
        assert config.name == "oua_auth"
        assert config.verbose_name == "Organization Unified Access Authentication"

    @patch("oua_auth.apps.post_migrate")
    @patch("oua_auth.logging_init.initialize_logging")
    def test_ready_success(self, mock_initialize_logging, mock_post_migrate):
        """Test the ready method successfully initializes components."""
        # Create config instance
        config = OUAAppConfig.__new__(OUAAppConfig)
        config.name = "oua_auth"

        # Mock the logging module for the ready method
        with patch("oua_auth.apps.logger") as mock_logger:
            # Call ready
            config.ready()

            # Verify logging was initialized
            mock_initialize_logging.assert_called_once()

            # Verify post_migrate signal was connected
            mock_post_migrate.connect.assert_called_once()

            # Verify logger message
            mock_logger.info.assert_called_with("OUA Auth application initialized")


class TestPostMigrationTasks:
    """Tests for post-migration tasks."""

    @pytest.mark.django_db
    @patch("oua_auth.token_blacklist.initialize_token_blacklist")
    def test_post_migration_tasks_token_blacklist(
        self, mock_initialize_token_blacklist
    ):
        """Test post-migration tasks initialize the token blacklist."""
        # Setup mock
        mock_initialize_token_blacklist.return_value = True

        # Mock logger to prevent output
        with patch("oua_auth.apps.logger") as mock_logger:
            # Call the post migration function directly with a mock sender
            perform_post_migration_tasks(MagicMock())

            # Verify token blacklist was initialized
            mock_initialize_token_blacklist.assert_called_once()

    @pytest.mark.django_db
    @patch(
        "oua_auth.token_blacklist.initialize_token_blacklist",
        side_effect=Exception("Test error"),
    )
    def test_post_migration_tasks_with_token_blacklist_exception(
        self, mock_initialize_token_blacklist
    ):
        """Test post-migration tasks handle token blacklist initialization exceptions."""
        # Mock logger to check warnings
        with patch("oua_auth.apps.logger") as mock_logger:
            # Call the post migration function
            perform_post_migration_tasks(MagicMock())

            # Verify attempt was made
            mock_initialize_token_blacklist.assert_called_once()

            # Verify warning was logged with correct message
            mock_logger.warning.assert_any_call(
                "Failed to initialize token blacklist: Test error"
            )

    @pytest.mark.django_db
    @patch("oua_auth.models.UserSecurityProfile")
    def test_post_migration_user_security_profiles(self, mock_user_security_profile):
        """Test post-migration tasks create security profiles."""
        # Setup mock
        mock_user_security_profile.auto_create_profiles.return_value = 5

        # Mock logger to check info message
        with patch("oua_auth.apps.logger") as mock_logger:
            # Call the post migration function
            perform_post_migration_tasks(MagicMock())

            # Verify profiles were created
            mock_user_security_profile.auto_create_profiles.assert_called_once()

            # Verify info message was logged
            mock_logger.info.assert_any_call("Created 5 missing user security profiles")
