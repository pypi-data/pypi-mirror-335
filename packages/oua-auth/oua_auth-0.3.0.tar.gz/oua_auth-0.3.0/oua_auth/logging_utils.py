"""
Logging utilities for OUA SSO Authentication.

This module provides structured logging capabilities with consistent formatting
for better integration with log management systems.
"""

import logging
import json
import traceback
import re
from typing import Any, Dict, Optional, List, Union
from functools import wraps
from datetime import datetime, UTC
import inspect
import uuid
from django.conf import settings
import os
import sys

# Default log levels
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_CONSOLE_LOG_LEVEL = "INFO"
DEFAULT_FILE_LOG_LEVEL = "DEBUG"

# Sensitive fields that should be redacted in logs
SENSITIVE_FIELDS = [
    "password",
    "token",
    "secret",
    "key",
    "authorization",
    "jwt",
    "access_token",
    "refresh_token",
    "private",
    "credentials",
]

# Regular expression for token pattern (to redact JWT tokens from logs)
TOKEN_PATTERN = re.compile(r"eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+")


class StructuredLogRecord(logging.LogRecord):
    """Extended LogRecord that supports structured logging."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_id = getattr(self, "request_id", None)
        self.user_id = getattr(self, "user_id", None)
        self.ip_address = getattr(self, "ip_address", None)
        self.component = getattr(self, "component", None)
        # Additional context for detailed debugging
        self.correlation_id = getattr(self, "correlation_id", None)
        self.trace_id = getattr(self, "trace_id", None)


class SensitiveDataFilter(logging.Filter):
    """Filter that redacts sensitive information from log messages."""

    def filter(self, record):
        if isinstance(record.msg, str):
            # Redact JWT tokens in strings
            record.msg = TOKEN_PATTERN.sub("[REDACTED_TOKEN]", record.msg)

        # Process extra data
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            self._redact_sensitive_data(record.extra)

        # Handle exc_info specially to ensure tracebacks don't contain sensitive data
        if record.exc_info:
            # Convert exception message to string and redact sensitive data
            try:
                exc_type, exc_value, exc_tb = record.exc_info
                if exc_value and hasattr(exc_value, "args") and exc_value.args:
                    # Create a copy of the exception with redacted message
                    redacted_args = list(exc_value.args)
                    for i, arg in enumerate(redacted_args):
                        if isinstance(arg, str):
                            redacted_args[i] = TOKEN_PATTERN.sub(
                                "[REDACTED_TOKEN]", arg
                            )

                    # Update the exception message
                    exc_value.args = tuple(redacted_args)
                    record.exc_info = (exc_type, exc_value, exc_tb)
            except Exception:
                # If redacting fails, keep the original exc_info
                pass

        return True

    def _redact_sensitive_data(self, data, path=""):
        """
        Recursively redact sensitive data in dictionaries.

        Args:
            data: Dictionary or list to redact
            path: Current path within nested structure for field name matching
        """
        if isinstance(data, dict):
            for key, value in list(data.items()):
                current_path = f"{path}.{key}" if path else key

                # Redact sensitive keys
                if any(sensitive in key.lower() for sensitive in SENSITIVE_FIELDS):
                    data[key] = "[REDACTED]"
                # Redact token strings
                elif isinstance(value, str) and TOKEN_PATTERN.search(value):
                    data[key] = TOKEN_PATTERN.sub("[REDACTED_TOKEN]", value)
                # Recursively process nested structures
                elif isinstance(value, (dict, list)):
                    self._redact_sensitive_data(value, current_path)

        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    self._redact_sensitive_data(item, path)
                elif isinstance(item, str) and TOKEN_PATTERN.search(item):
                    data[i] = TOKEN_PATTERN.sub("[REDACTED_TOKEN]", item)


class JSONFormatter(logging.Formatter):
    """Formatter for structured JSON logs."""

    def __init__(self, include_timestamp=True, indent=None, sort_keys=False):
        """
        Initialize the JSON formatter.

        Args:
            include_timestamp: Whether to include a timestamp
            indent: JSON indent for pretty printing (None for compact)
            sort_keys: Whether to sort JSON keys
        """
        super().__init__()
        self.include_timestamp = include_timestamp
        self.indent = indent
        self.sort_keys = sort_keys

    def format(self, record):
        """Format the log record as JSON."""
        log_data = {
            # Standard log record attributes
            "level": record.levelname,
            "time": datetime.now(UTC).isoformat(),
            "name": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process_id": record.process,
            "thread_id": record.thread,
            "message": record.getMessage(),
        }

        # Add context data if available
        for attr in [
            "request_id",
            "user_id",
            "ip_address",
            "component",
            "correlation_id",
            "trace_id",
        ]:
            if hasattr(record, attr) and getattr(record, attr) is not None:
                log_data[attr] = getattr(record, attr)

        # Add extra data if available
        if hasattr(record, "extra") and record.extra:
            log_data["extra"] = record.extra

        # Add exception info if available
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }

        return json.dumps(log_data, indent=self.indent, sort_keys=self.sort_keys)


class ContextLogger:
    """
    Enhanced logger with support for context-rich structured logging.

    This class wraps a standard logger with methods that support structured
    logging with context data.
    """

    def __init__(self, name):
        """Initialize with logger name."""
        self.logger = logging.getLogger(name)
        self.default_context = {}

        # Get default instance_id for all logs from this logger
        self.instance_id = str(uuid.uuid4())[:8]

    def with_context(self, **kwargs):
        """Create a new logger with default context values."""
        new_logger = ContextLogger(self.logger.name)
        new_logger.default_context = self.default_context.copy()
        new_logger.default_context.update(kwargs)
        return new_logger

    def _process_args(self, msg, extra=None, **kwargs):
        """Process and merge context data."""
        # Start with default context
        context = self.default_context.copy()

        # Add/override with explicit context
        if extra:
            context.update(extra)

        # Add caller information for better traceability
        frame = (
            inspect.currentframe().f_back.f_back
        )  # Skip _process_args and the log method
        context.setdefault("source_module", frame.f_globals.get("__name__"))
        context.setdefault("source_function", frame.f_code.co_name)
        context.setdefault("source_line", frame.f_lineno)

        # Set default component based on module name if not specified
        if "component" not in context and "source_module" in context:
            module_parts = context["source_module"].split(".")
            context["component"] = (
                module_parts[-1] if len(module_parts) > 0 else "unknown"
            )

        # Add instance_id for tracking unique logger instances
        context.setdefault("instance_id", self.instance_id)

        return msg, {"extra": context}

    # Standard logging methods with context support
    def debug(self, msg, *args, extra=None, **kwargs):
        msg, kwargs = self._process_args(msg, extra, **kwargs)
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, extra=None, **kwargs):
        msg, kwargs = self._process_args(msg, extra, **kwargs)
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, extra=None, **kwargs):
        msg, kwargs = self._process_args(msg, extra, **kwargs)
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, extra=None, **kwargs):
        msg, kwargs = self._process_args(msg, extra, **kwargs)
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, extra=None, **kwargs):
        msg, kwargs = self._process_args(msg, extra, **kwargs)
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg, *args, extra=None, **kwargs):
        msg, kwargs = self._process_args(msg, extra, **kwargs)
        self.logger.exception(msg, *args, **kwargs)

    # Alias for warning to match Python's logging module
    warn = warning


def setup_logging(name: str = None) -> ContextLogger:
    """
    Get a configured logger with the specified name.

    Args:
        name: Logger name (defaults to module name)

    Returns:
        ContextLogger: A configured logger instance
    """
    if name is None:
        # Get the calling module's name
        frame = inspect.currentframe().f_back
        name = frame.f_globals.get("__name__")

    return ContextLogger(name)


def configure_oua_logging(
    verbosity: str = None,
    file_path: str = None,
    json_output: bool = None,
    console_output: bool = None,
) -> None:
    """
    Configure logging for OUA SSO Authentication.

    This function sets up logging according to the provided parameters, or
    using values from Django settings if not provided.

    Args:
        verbosity: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        file_path: Path to log file (None for no file logging)
        json_output: Whether to output logs as JSON (default: True)
        console_output: Whether to output logs to console (default: True)
    """
    # Get configuration from settings or use defaults
    settings_verbosity = getattr(settings, "OUA_LOG_LEVEL", DEFAULT_LOG_LEVEL)
    settings_file_path = getattr(settings, "OUA_LOG_FILE", None)
    settings_json_output = getattr(settings, "OUA_LOG_JSON", True)
    settings_console_output = getattr(settings, "OUA_LOG_CONSOLE", True)

    # Override with provided parameters if given
    verbosity = verbosity or settings_verbosity
    file_path = file_path or settings_file_path
    json_output = json_output if json_output is not None else settings_json_output
    console_output = (
        console_output if console_output is not None else settings_console_output
    )

    # Convert string verbosity to logging level
    log_level = getattr(logging, verbosity.upper()) if verbosity else logging.INFO

    # Configure logging
    logger_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": JSONFormatter,
            },
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            },
        },
        "filters": {
            "sensitive_data": {
                "()": SensitiveDataFilter,
            },
        },
        "handlers": {},
        "loggers": {
            "": {  # Root logger
                "handlers": [],
                "level": log_level,
                "propagate": True,
            },
            "oua_auth": {
                "handlers": [],
                "level": log_level,
                "propagate": False,
            },
        },
    }

    # Add console handler if enabled
    if console_output:
        console_formatter = "json" if json_output else "standard"
        console_handler = {
            "class": "logging.StreamHandler",
            "formatter": console_formatter,
            "filters": ["sensitive_data"],
            "level": getattr(
                settings, "OUA_CONSOLE_LOG_LEVEL", DEFAULT_CONSOLE_LOG_LEVEL
            ),
            "stream": sys.stdout,
        }
        logger_config["handlers"]["console"] = console_handler
        logger_config["loggers"][""]["handlers"].append("console")
        logger_config["loggers"]["oua_auth"]["handlers"].append("console")

    # Add file handler if path is provided
    if file_path:
        # Ensure log directory exists
        log_dir = os.path.dirname(file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        file_formatter = "json" if json_output else "standard"
        file_handler = {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": file_formatter,
            "filters": ["sensitive_data"],
            "level": getattr(settings, "OUA_FILE_LOG_LEVEL", DEFAULT_FILE_LOG_LEVEL),
            "filename": file_path,
            "when": "midnight",
            "backupCount": 14,  # Keep logs for 14 days
        }
        logger_config["handlers"]["file"] = file_handler
        logger_config["loggers"][""]["handlers"].append("file")
        logger_config["loggers"]["oua_auth"]["handlers"].append("file")

    # Apply the logging configuration
    logging.config.dictConfig(logger_config)

    # Configure LogRecord factory for structured logging
    logging.setLogRecordFactory(StructuredLogRecord)

    # Log the configuration
    logger = logging.getLogger("oua_auth.setup")
    logger.info(
        f"OUA logging configured: level={verbosity}, json={json_output}, "
        f"console={console_output}, file={file_path}"
    )


def log_request(logger=None):
    """
    Decorator to log request information.

    This decorator logs the beginning and end of request processing,
    including timing information.

    Args:
        logger: Logger to use (will be created if not provided)
    """

    def decorator(view_func):
        if logger is None:
            log = setup_logging(view_func.__module__)
        else:
            log = logger

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Generate request ID if not already present
            request_id = getattr(request, "id", str(uuid.uuid4()))
            setattr(request, "id", request_id)

            # Create request context
            context = {
                "request_id": request_id,
                "ip_address": _get_client_ip(request),
                "method": request.method,
                "path": request.path,
            }

            # Add user ID if authenticated
            if hasattr(request, "user") and getattr(
                request.user, "is_authenticated", False
            ):
                context["user_id"] = getattr(request.user, "id", None)
                context["user_email"] = getattr(request.user, "email", None)

            # Log request start
            start_time = datetime.now(UTC)
            log.info(f"Request started: {request.method} {request.path}", extra=context)

            try:
                # Call the view
                response = view_func(request, *args, **kwargs)

                # Log request completion
                duration_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000
                context["duration_ms"] = duration_ms
                context["status_code"] = getattr(response, "status_code", 0)
                log.info(
                    f"Request completed: {request.method} {request.path} "
                    f"-> {context['status_code']} ({duration_ms:.2f}ms)",
                    extra=context,
                )
                return response

            except Exception as e:
                # Log request error
                duration_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000
                context["duration_ms"] = duration_ms
                context["error"] = str(e)
                context["error_type"] = type(e).__name__
                log.exception(
                    f"Request failed: {request.method} {request.path} "
                    f"-> {type(e).__name__}: {str(e)} ({duration_ms:.2f}ms)",
                    extra=context,
                )
                raise

        return wrapper

    return decorator


def _get_client_ip(request):
    """Extract client IP address from request."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR", "unknown")
    return ip
