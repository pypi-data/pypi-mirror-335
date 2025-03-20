"""Tests for logging utilities."""

import pytest
import json
import logging
from unittest.mock import MagicMock, patch
import io
import sys
import time
from django.test import RequestFactory
from django.http import HttpResponse
from django.contrib.auth.models import AnonymousUser, User

from oua_auth.logging_utils import (
    setup_logging,
    configure_oua_logging,
    log_request,
    ContextLogger,
    JSONFormatter,
    SensitiveDataFilter,
)


class TestLoggingUtilities:
    """Tests for logging utilities."""

    def test_setup_logging(self):
        """Test setup_logging function."""
        logger = setup_logging("test_logger")
        assert isinstance(logger, ContextLogger)
        assert logger.logger.name == "test_logger"

    def test_context_logger_with_context(self):
        """Test ContextLogger.with_context method."""
        logger = setup_logging("test_logger")
        context_logger = logger.with_context(user_id=123, request_id="req-123")

        assert context_logger.default_context["user_id"] == 123
        assert context_logger.default_context["request_id"] == "req-123"

    def test_sensitive_data_filter(self):
        """Test SensitiveDataFilter."""
        filter_instance = SensitiveDataFilter()

        # Create a test token
        test_token = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

        # Create a log record with sensitive data
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=f"Token: {test_token}",
            args=(),
            exc_info=None,
        )

        # Add extra data with sensitive information
        setattr(
            record,
            "extra",
            {
                "password": "supersecret",
                "token": test_token,
                "user": {"api_key": "secret-key-123"},
            },
        )

        # Apply filter
        filter_instance.filter(record)

        # Check that sensitive data was redacted
        assert test_token not in record.msg
        assert "[REDACTED_TOKEN]" in record.msg
        assert record.extra["password"] == "[REDACTED]"
        # The token field itself is redacted completely since it contains 'token' in the key name
        assert record.extra["token"] == "[REDACTED]"
        assert record.extra["user"]["api_key"] == "[REDACTED]"

    def test_json_formatter(self):
        """Test JSONFormatter."""
        formatter = JSONFormatter()

        # Create a log record
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.request_id = "req-123"
        record.user_id = 456
        record.extra = {"action": "login"}

        # Format the record
        formatted = formatter.format(record)

        # Parse the JSON to verify
        log_data = json.loads(formatted)

        assert log_data["level"] == "INFO"
        assert log_data["message"] == "Test message"
        assert log_data["request_id"] == "req-123"
        assert log_data["user_id"] == 456
        assert log_data["extra"]["action"] == "login"

    def test_custom_logging(self):
        """Test that we can configure and use a logger directly."""
        # Create a test-specific handler
        test_stream = io.StringIO()
        handler = logging.StreamHandler(test_stream)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter("%(message)s"))

        # Get a logger and add our handler
        logger_name = f"test_logger_{time.time()}"
        test_logger = logging.getLogger(logger_name)
        test_logger.setLevel(logging.DEBUG)
        test_logger.addHandler(handler)
        test_logger.propagate = False

        # Log a test message
        test_message = f"Test debug message {time.time()}"
        test_logger.debug(test_message)

        # Check the output
        output = test_stream.getvalue()
        assert test_message in output

    def test_log_request_decorator(self):
        """Test log_request decorator."""
        logger = MagicMock()

        # Create a view function with the decorator
        @log_request(logger=logger)
        def test_view(request):
            return HttpResponse("Test response")

        # Create a test request
        request = RequestFactory().get("/test")
        request.user = AnonymousUser()

        # Call the view
        response = test_view(request)

        # Check that the logger was called for request start and completion
        assert logger.info.call_count == 2
        start_call_args = logger.info.call_args_list[0][0][0]
        end_call_args = logger.info.call_args_list[1][0][0]

        assert "Request started" in start_call_args
        assert "Request completed" in end_call_args
        assert response.content == b"Test response"

    def test_log_request_decorator_with_exception(self):
        """Test log_request decorator with exception."""
        logger = MagicMock()

        # Create a view function with the decorator that raises an exception
        @log_request(logger=logger)
        def test_view(request):
            raise ValueError("Test exception")

        # Create a test request
        request = RequestFactory().get("/test")
        request.user = AnonymousUser()

        # Call the view (should raise exception)
        with pytest.raises(ValueError):
            test_view(request)

        # Check that the logger was called for request start and failure
        assert logger.info.call_count == 1
        assert logger.exception.call_count == 1
        start_call_args = logger.info.call_args_list[0][0][0]
        exception_call_args = logger.exception.call_args_list[0][0][0]

        assert "Request started" in start_call_args
        assert "Request failed" in exception_call_args
        assert "Test exception" in exception_call_args
