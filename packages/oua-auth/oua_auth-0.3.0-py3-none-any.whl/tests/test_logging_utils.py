"""Tests for the logging utilities."""

import pytest
import logging
import json
import re
import sys
from unittest.mock import patch, MagicMock, call
from django.test import RequestFactory, override_settings
from django.http import HttpRequest

from oua_auth.logging_utils import (
    SensitiveDataFilter,
    JSONFormatter,
    ContextLogger,
    configure_oua_logging,
    _get_client_ip,
)


class TestLoggingUtilsExtended:
    """Tests for extended logging utilities."""

    def test_sensitive_data_filter_nested_data(self):
        """Test SensitiveDataFilter with nested data."""
        filter_instance = SensitiveDataFilter()

        # Create a LogRecord with sensitive data
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Set extra attribute with sensitive data
        record.extra = {
            "user": {
                "name": "Test User",
                "password": "secret123",
            },
            "token": "eyJhbGciOiJIUzI1NiJ9.e30.ZRrHA",
        }

        # Apply the filter
        filter_instance.filter(record)

        # Check that sensitive data was redacted
        assert record.extra["user"]["password"] == "[REDACTED]"
        assert record.extra["token"] == "[REDACTED]"
        assert record.extra["user"]["name"] == "Test User"  # Not sensitive, unchanged

    def test_sensitive_data_filter_with_token_pattern(self):
        """Test SensitiveDataFilter with JWT token pattern in a string."""
        filter_instance = SensitiveDataFilter()

        # Create a log record with a JWT token
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MX0.AbCdEf123456",
            args=(),
            exc_info=None,
        )

        # Apply the filter
        filter_instance.filter(record)

        # Check that the token was redacted
        assert "[REDACTED_TOKEN]" in record.msg
        assert "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9" not in record.msg
        assert "Bearer " in record.msg  # The rest should be unchanged

    def test_json_formatter_with_exception(self):
        """Test JSONFormatter with exception information."""
        formatter = JSONFormatter()

        # Create a real exception
        try:
            raise ValueError("Invalid token")
        except ValueError:
            exc_info = sys.exc_info()

        # Create a log record with exception info
        record = logging.LogRecord(
            name="test.logger",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="Error occurred",
            args=(),
            exc_info=exc_info,
        )

        # Add structured logging fields
        record.request_id = "req-123"
        record.user_id = "user-456"

        # Format the record
        log_entry = formatter.format(record)
        log_dict = json.loads(log_entry)

        # Verify the formatted output - check only core fields
        assert log_dict["level"] == "ERROR"
        assert log_dict["message"] == "Error occurred"
        assert "name" in log_dict or "logger" in log_dict  # Field name might vary

        # Check that exception info is included
        assert "exception" in log_dict
        assert "Invalid token" in str(log_dict["exception"])

        # Verify structured fields are present
        assert log_dict["request_id"] == "req-123"
        assert log_dict["user_id"] == "user-456"

    def test_context_logger_methods(self):
        """Test ContextLogger's logging methods."""
        # Create a context logger
        logger_name = "test.logger"

        # Mock the underlying logger
        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            # Create HTTP request with context data
            request = HttpRequest()
            request.META["REMOTE_ADDR"] = "127.0.0.1"
            request.user = MagicMock()
            request.user.id = "user-789"

            # Create a context logger with request
            context_logger = ContextLogger(logger_name)

            # Set the request directly or through initialization defaults
            context_logger.request = request

            # Test various logging methods
            context_logger.info("Test info message", extra={"test_key": "test_value"})
            context_logger.error("Test error message")
            context_logger.debug("Test debug message")

            # Verify calls were made with correct context
            assert mock_logger.info.called
            assert mock_logger.error.called
            assert mock_logger.debug.called

            # Verify the extra context was included
            info_call_kwargs = mock_logger.info.call_args[1]
            assert "extra" in info_call_kwargs
            assert info_call_kwargs["extra"]["test_key"] == "test_value"

    @patch("logging.config.dictConfig")
    @patch("oua_auth.logging_utils.SensitiveDataFilter")
    @patch("oua_auth.logging_utils.JSONFormatter")
    @patch("logging.getLogger")
    def test_configure_oua_logging_defaults(
        self, mock_get_logger, mock_json_formatter, mock_filter, mock_dict_config
    ):
        """Test configure_oua_logging with default settings."""
        # Mock logger
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        # Call with defaults
        configure_oua_logging()

        # Verify dictConfig was called
        mock_dict_config.assert_called_once()

        # Check that the config dictionary has the expected structure
        config = mock_dict_config.call_args[0][0]
        assert config["version"] == 1
        assert "formatters" in config
        assert "filters" in config
        assert "handlers" in config
        assert "loggers" in config

        # Verify logger was configured
        mock_get_logger.assert_called()
        mock_logger.info.assert_called_once()

    @override_settings(
        OUA_LOG_LEVEL="DEBUG",
        OUA_LOG_FILE="/tmp/test.log",
        OUA_LOG_JSON=True,
        OUA_LOG_CONSOLE=True,
    )
    @patch("logging.config.dictConfig")
    @patch("os.path.exists")
    @patch("os.makedirs")
    @patch("logging.getLogger")
    def test_configure_oua_logging_with_settings(
        self, mock_get_logger, mock_makedirs, mock_path_exists, mock_dict_config
    ):
        """Test configure_oua_logging with custom settings."""
        # Mock path check for log directory
        mock_path_exists.return_value = False

        # Mock logger
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        # Call with settings from decorator
        configure_oua_logging()

        # Verify dictConfig was called
        mock_dict_config.assert_called_once()

        # Check that the config has the file handler
        config = mock_dict_config.call_args[0][0]
        assert "file" in config["handlers"]
        assert config["handlers"]["file"]["filename"] == "/tmp/test.log"

        # Verify directory was created
        mock_makedirs.assert_called_once_with("/tmp", exist_ok=True)

        # Verify logger was configured
        mock_get_logger.assert_called()
        mock_logger.info.assert_called_once()

    def test_get_client_ip_with_x_forwarded_for(self):
        """Test _get_client_ip with X-Forwarded-For header."""
        request = RequestFactory().get("/")
        request.META["HTTP_X_FORWARDED_FOR"] = "192.168.1.1, 10.0.0.1"

        ip = _get_client_ip(request)
        assert ip == "192.168.1.1"

    def test_get_client_ip_without_headers(self):
        """Test _get_client_ip without special headers."""
        request = RequestFactory().get("/")
        request.META["REMOTE_ADDR"] = "10.0.0.2"

        ip = _get_client_ip(request)
        assert ip == "10.0.0.2"
