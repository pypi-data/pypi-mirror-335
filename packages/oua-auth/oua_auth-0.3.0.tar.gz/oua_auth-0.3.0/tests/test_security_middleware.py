"""Tests for the security headers middleware."""

import pytest
from django.http import HttpResponse
from django.test import RequestFactory, override_settings

from oua_auth.security_middleware import SecurityHeadersMiddleware


@pytest.fixture
def fake_request():
    """Create a fake request for testing the middleware."""
    factory = RequestFactory()
    return factory.get("/test-path/")


def get_middleware(settings_dict=None):
    """Create a middleware instance with specified settings."""

    def get_response(request):
        # Dummy view that returns a response
        return HttpResponse("Test response")

    middleware = SecurityHeadersMiddleware(get_response)

    # Mock the _get_setting method to return values from settings_dict if provided
    if settings_dict:
        original_get_setting = middleware._get_setting

        def mock_get_setting(name, default=None):
            if name in settings_dict:
                return settings_dict[name]
            return original_get_setting(name, default)

        middleware._get_setting = mock_get_setting

    return middleware


class TestSecurityHeadersMiddleware:
    """Tests for the SecurityHeadersMiddleware."""

    def test_default_security_headers(self, fake_request):
        """Test that the middleware adds default security headers to the response."""
        middleware = get_middleware()
        response = middleware(fake_request)

        # Check that the default headers are set
        assert response["X-Frame-Options"] == "SAMEORIGIN"
        assert response["X-XSS-Protection"] == "1; mode=block"
        assert response["X-Content-Type-Options"] == "nosniff"
        assert response["Referrer-Policy"] == "strict-origin-when-cross-origin"
        assert (
            response["Permissions-Policy"]
            == "geolocation=(), microphone=(), camera=(), payment=()"
        )
        assert (
            response["Content-Security-Policy"]
            == "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'"
        )

        # HSTS should be off by default
        assert "Strict-Transport-Security" not in response

    def test_hsts_header(self, fake_request):
        """Test that the middleware adds HSTS header when enabled."""
        middleware = get_middleware({"OUA_ENABLE_HSTS": True})
        response = middleware(fake_request)

        # Check that HSTS is enabled with default settings
        assert (
            response["Strict-Transport-Security"]
            == "max-age=31536000; includeSubDomains"
        )

    def test_custom_hsts_header(self, fake_request):
        """Test that the middleware adds HSTS header with custom settings."""
        middleware = get_middleware(
            {
                "OUA_ENABLE_HSTS": True,
                "OUA_HSTS_SECONDS": 86400,  # 1 day
                "OUA_HSTS_INCLUDE_SUBDOMAINS": False,
                "OUA_HSTS_PRELOAD": True,
            }
        )
        response = middleware(fake_request)

        # Check that HSTS is enabled with custom settings
        assert response["Strict-Transport-Security"] == "max-age=86400; preload"

    def test_custom_csp_header(self, fake_request):
        """Test that the middleware adds a custom Content Security Policy."""
        middleware = get_middleware(
            {"OUA_CONTENT_SECURITY_POLICY": "default-src 'self' https://example.com"}
        )
        response = middleware(fake_request)

        # Check that CSP has custom value
        assert (
            response["Content-Security-Policy"]
            == "default-src 'self' https://example.com"
        )

    def test_custom_security_headers(self, fake_request):
        """Test that the middleware adds custom security headers."""
        middleware = get_middleware(
            {
                "OUA_FRAME_OPTIONS": "DENY",
                "OUA_XSS_PROTECTION": "0",
                "OUA_CONTENT_TYPE_OPTIONS": "",  # Disable this header
                "OUA_REFERRER_POLICY": "no-referrer",
                "OUA_PERMISSIONS_POLICY": "",  # Disable this header
            }
        )
        response = middleware(fake_request)

        # Check custom header values
        assert response["X-Frame-Options"] == "DENY"
        assert response["X-XSS-Protection"] == "0"
        assert "X-Content-Type-Options" not in response
        assert response["Referrer-Policy"] == "no-referrer"
        assert "Permissions-Policy" not in response

    def test_excluded_paths(self, fake_request):
        """Test that the middleware skips excluded paths."""
        middleware = get_middleware(
            {"OUA_SECURITY_HEADERS_EXCLUDE_PATHS": ["/test-path/"]}
        )
        response = middleware(fake_request)

        # Check that no security headers are added for excluded paths
        assert "X-Frame-Options" not in response
        assert "X-XSS-Protection" not in response
        assert "X-Content-Type-Options" not in response
        assert "Referrer-Policy" not in response
        assert "Permissions-Policy" not in response
        assert "Content-Security-Policy" not in response
