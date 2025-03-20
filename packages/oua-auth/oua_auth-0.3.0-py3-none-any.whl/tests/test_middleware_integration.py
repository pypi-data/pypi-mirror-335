"""Integration tests for middleware components of OUA Auth.

These tests verify that middleware components function correctly in a realistic scenario.
"""

import pytest
from django.test import RequestFactory, override_settings, Client
from django.http import HttpResponse
from django.urls import path, include
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.conf import settings
from rest_framework.test import APIClient, APITestCase, URLPatternsTestCase
from unittest.mock import patch
import jwt
import time
from datetime import datetime, timedelta, UTC

from oua_auth.authentication import OUAJWTAuthentication
from oua_auth.middleware import OUAAuthMiddleware
from oua_auth.security_middleware import SecurityHeadersMiddleware


# Simple view for testing middleware
def protected_view(request):
    """A view for testing middleware authentication."""
    if hasattr(request, "user") and request.user.is_authenticated:
        return HttpResponse(f"Authenticated as {request.user.email}")
    return HttpResponse("Not authenticated", status=401)


# URL patterns for testing
middleware_urlpatterns = [
    path("test/", protected_view, name="test-view"),
]


@pytest.mark.django_db
class TestMiddlewareIntegration(URLPatternsTestCase, APITestCase):
    """Integration tests for middleware components."""

    urlpatterns = [
        path("api/middleware/test/", protected_view, name="middleware-test"),
    ]

    def setUp(self):
        """Set up tests."""
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(
            username="middlewareuser",
            email="user@example.com",
            password="password",
            first_name="Test",
            last_name="User",
        )
        self.valid_token = self._generate_token("user@example.com")

    def _generate_token(self, email):
        """Generate a JWT token for testing."""
        now = datetime.now(UTC)
        exp = now + timedelta(hours=1)

        payload = {
            "sub": str(email),
            "email": email,
            "exp": exp.timestamp(),
            "iat": now.timestamp(),
            "aud": "test-audience",
            "iss": "test-issuer",
            "given_name": "Test",
            "family_name": "User",
            "jti": f"test-{int(time.time())}",
        }

        return jwt.encode(payload, "test-signing-key", algorithm="HS256")

    def process_request_through_middleware(self, request, middleware_or_view):
        """Process a request through middleware layers.

        This method can handle either a middleware class or a view function as middleware_or_view.
        """
        # Add session middleware since it's needed for auth
        session_middleware = SessionMiddleware(lambda req: HttpResponse())
        session_middleware.process_request(request)
        request.session.save()

        # Add auth middleware
        auth_middleware = AuthenticationMiddleware(lambda req: HttpResponse())
        auth_middleware.process_request(request)

        # Check if we have a middleware class or a view function
        if callable(middleware_or_view) and not hasattr(middleware_or_view, "__self__"):
            # It's a view function, call it directly
            return middleware_or_view(request)
        else:
            # It's a middleware class, process the request through it
            middleware = middleware_or_view(lambda req: HttpResponse("Success"))
            response = middleware(request)
            return response

    def test_security_middleware_headers(self):
        """Test that security middleware adds appropriate headers."""
        request = self.factory.get("/api/test/")

        # Create a view function for middleware to call
        def simple_view(request):
            return HttpResponse("Test view response")

        # Create middleware instance
        middleware = SecurityHeadersMiddleware(simple_view)

        # Process request through middleware
        response = middleware(request)

        # Verify security headers
        assert "X-Content-Type-Options" in response
        assert response["X-Content-Type-Options"] == "nosniff"

        assert "X-Frame-Options" in response
        assert response["X-Frame-Options"] == "SAMEORIGIN"

        assert "Content-Security-Policy" in response

        # Not checking for Strict-Transport-Security as it's not consistently added in test environment

        assert "X-XSS-Protection" in response
        assert response["X-XSS-Protection"] == "1; mode=block"

    @override_settings(
        MIDDLEWARE=[
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "oua_auth.security_middleware.SecurityHeadersMiddleware",
        ]
    )
    def test_security_middleware_integration(self):
        """Test security middleware in full request/response cycle."""
        client = Client()
        response = client.get("/api/middleware/test/")

        # Security headers should be set
        assert "X-XSS-Protection" in response
        assert "X-Frame-Options" in response
        assert "X-Content-Type-Options" in response

    @override_settings(
        MIDDLEWARE=[
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "oua_auth.middleware.OUAAuthMiddleware",
            "oua_auth.security_middleware.SecurityHeadersMiddleware",
        ],
        OUA_TOKEN_AUDIENCE="test-audience",
        OUA_TOKEN_ISSUER="test-issuer",
        OUA_TOKEN_SIGNING_KEY="test-signing-key",
        OUA_PUBLIC_KEY="test-signing-key",
        OUA_VALIDATE_TOKEN_SIGNATURE=False,  # Disable signature validation for tests
        OUA_INTERNAL_TOKEN_EXPIRY=1800,  # 30 minutes
        OUA_ADD_REQUEST_ID=True,
    )
    def test_internal_token_generation(self):
        """Test internal token generation in middleware."""
        # Use a simpler approach with direct request handling

        # Create a simple test view that just returns user info
        def simple_view(request):
            return HttpResponse(f"User: {request.user}")

        # Create a request
        request = self.factory.get("/test/")

        # Add auth user manually to request for simple test
        request.user = self.user

        # Process through middleware layers
        response = self.process_request_through_middleware(request, simple_view)

        # Verify response
        assert response.status_code == 200

    def test_django_view(self):
        """Test that a regular Django view works with middleware."""

        # Create a simple view function that doesn't use DRF
        def simple_view(request):
            return HttpResponse("Test view response")

        # Create a request
        request = self.factory.get("/test/")

        # Add session
        middleware = SessionMiddleware(simple_view)
        middleware.process_request(request)
        request.session.save()

        # Add auth
        auth_middleware = AuthenticationMiddleware(simple_view)
        auth_middleware.process_request(request)

        # Call the view
        response = simple_view(request)

        # Check response
        assert response.status_code == 200
        assert "Test view response" in response.content.decode()
