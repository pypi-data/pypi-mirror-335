"""Test fixtures for OUA authentication tests."""

import json
import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest
import jwt  # Using PyJWT instead of python-jose for testing
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest
from rest_framework.request import Request

# RSA keys for testing - properly formatted
# Private key for signing
RSA_PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAnzyis1ZjfNB0bBgKFMSvvkTtwlvBsaJq7S5wA+kzeVOVpVWw
kWdVha4s38XM/pa/yr47av7+z3VTmvDRyAHcaT92whREFpLv9cj5lTeJSibyr/Mr
m/YtjCZVWgaOYIhwrXwKLqPr/11inWsAkfIytvHWTxZYEcXLgAXFuUuaS3uF9gEi
NQwzGTU1v0FqkqTBr4B8nW3HCN47XUu0t8Y0e+lf4s4OxQawWD79J9/5d3Ry0vbV
3Am1FtGJiJvOwRsIfVChDpYStTcHTCMqtvWbV6L11BWkpzGXSW4Hv43qa+GSYOD2
QU68Mb59oSk2OB+BtOLpJofmbGEGgvmwyCI9MwIDAQABAoIBACiARq2wkltjtcjs
kFvZ7w1JAORHbEufEO1Eu27zOIlqbgyAcAl7q+/1bip4Z/x1IVES84/yTaM8p0go
amMhvgry/mS8vNi1BN2SAZEnb/7xSxbflb70bX9RHLJqKnp5GZe2jexw+wyXlwaM
+bclUCrh9e1ltH7IvUrRrQnFJfh+is1fRon9Co9Li0GwoN0x0byrrngU8Ak3Y6D9
D8GjQA4Elm94ST3izJv8iCOLSDBmzsPsXfcCUZfmTfZ5DbUDMbMxRnSo3nQeoKGC
0Lj9FkWcfmLcpGlSXTO+Ww1L7EGq+PT3NtRae1FZPwjddQ1/4V905kyQFLamAA5Y
lSpE2wkCgYEAy1OPLQcZt4NQnQzPz2SBJqQN2P5u3vXl+zNVKP8w4eBv0vWuJJF+
hkGNnSxXQrTkvDOIUddSKOzHHgSg4nY6K02ecyT0PPm/UZvtRpWrnBjcEVtHEJNp
bU9pLD5iZ0J9sbzPU/LxPmuAP2Bs8JmTn6aFRspFrP7W0s1Nmk2jsm0CgYEAyH0X
+jpoqxj4efZfkUrg5GbSEhf+dZglf0tTOA5bVg8IYwtmNk/pniLG/zI7c+GlTc9B
BwfMr59EzBq/eFMI7+LgXaVUsM/sS4Ry+yeK6SJx/otIMWtDfqxsLD8CPMCRvecC
2Pip4uSgrl0MOebl9XKp57GoaUWRWRHqwV4Y6h8CgYAZhI4mh4qZtnhKjY4TKDjx
QYufXSdLAi9v3FxmvchDwOgn4L+PRVdMwDNms2bsL0m5uPn104EzM6w1vzz1zwKz
5pTpPI0OjgWN13Tq8+PKvm/4Ga2MjgOgPWQkslulO/oMcXbPwWC3hcRdr9tcQtn9
Imf9n2spL/6EDFId+Hp/7QKBgAqlWdiXsWckdE1Fn91/NGHsc8syKvjjk1onDcw0
NvVi5vcba9oGdElJX3e9mxqUKMrw7msJJv1MX8LWyMQC5L6YNYHDfbPF1q5L4i8j
8mRex97UVokJQRRA452V2vCO6S5ETgpnad36de3MUxHgCOX3qL382Qx9/THVmbma
3YfRAoGAUxL/Eu5yvMK8SAt/dJK6FedngcM3JEFNplmtLYVLWhkIlNRGDwkg3I5K
y18Ae9n7dHVueyslrb6weq7dTkYDi3iOYRW8HRkIQh06wEdbxt0shTzAJvvCQfrB
jg/3747WSsf/zBTcHihTRBdAv6OmdhV4/dD5YBfLAkLrd+mX7iE=
-----END RSA PRIVATE KEY-----"""

# Public key for verification
RSA_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnzyis1ZjfNB0bBgKFMSv
vkTtwlvBsaJq7S5wA+kzeVOVpVWwkWdVha4s38XM/pa/yr47av7+z3VTmvDRyAHc
aT92whREFpLv9cj5lTeJSibyr/Mrm/YtjCZVWgaOYIhwrXwKLqPr/11inWsAkfIy
tvHWTxZYEcXLgAXFuUuaS3uF9gEiNQwzGTU1v0FqkqTBr4B8nW3HCN47XUu0t8Y0
e+lf4s4OxQawWD79J9/5d3Ry0vbV3Am1FtGJiJvOwRsIfVChDpYStTcHTCMqtvWb
V6L11BWkpzGXSW4Hv43qa+GSYOD2QU68Mb59oSk2OB+BtOLpJofmbGEGgvmwyCI9
MwIDAQAB
-----END PUBLIC KEY-----"""

User = get_user_model()


@pytest.fixture
def mock_request():
    """Create a mocked Django HttpRequest."""
    request = HttpRequest()
    request.META = {}
    request.headers = {}
    request.user = AnonymousUser()
    return request


@pytest.fixture
def drf_request(mock_request):
    """Create a mocked DRF Request object."""
    return Request(mock_request)


@pytest.fixture
@pytest.mark.django_db
def user_regular():
    """Create a regular user for testing."""
    return User.objects.create_user(
        username="testuser",
        email="user@example.com",
        password="password123",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
@pytest.mark.django_db
def user_admin():
    """Create an admin user for testing."""
    return User.objects.create_user(
        username="adminuser",
        email="admin@example.com",
        password="password123",
        first_name="Admin",
        last_name="User",
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture
def jwt_payload_regular():
    """Create a JWT payload for a regular user."""
    now = int(time.time())
    return {
        "sub": "user123",
        "email": "user@example.com",
        "given_name": "Test",
        "family_name": "User",
        "roles": ["user"],
        "aud": "test-client-id",
        "iss": "https://test-sso.example.com",
        "iat": now,
        "exp": now + 3600,  # 1 hour later
    }


@pytest.fixture
def jwt_payload_admin():
    """Create a JWT payload for an admin user."""
    now = int(time.time())
    return {
        "sub": "admin123",
        "email": "admin@example.com",
        "given_name": "Admin",
        "family_name": "User",
        "roles": ["user", "admin"],
        "aud": "test-client-id",
        "iss": "https://test-sso.example.com",
        "iat": now,
        "exp": now + 3600,  # 1 hour later
    }


@pytest.fixture
def jwt_payload_admin_untrusted():
    """Create a JWT payload for an admin user with untrusted email."""
    now = int(time.time())
    return {
        "sub": "admin456",
        "email": "admin@untrusted-domain.com",
        "given_name": "Untrusted",
        "family_name": "Admin",
        "roles": ["user", "admin"],
        "aud": "test-client-id",
        "iss": "https://test-sso.example.com",
        "iat": now,
        "exp": now + 3600,  # 1 hour later
    }


@pytest.fixture
def jwt_payload_trusted_domain():
    """Create a JWT payload for a user with trusted domain email."""
    now = int(time.time())
    return {
        "sub": "user789",
        "email": "user@trusted.example.com",
        "given_name": "Trusted",
        "family_name": "User",
        "roles": ["user", "admin"],
        "aud": "test-client-id",
        "iss": "https://test-sso.example.com",
        "iat": now,
        "exp": now + 3600,  # 1 hour later
    }


@pytest.fixture
def jwt_payload_expired():
    """Create an expired JWT payload."""
    now = int(time.time())
    return {
        "sub": "user123",
        "email": "user@example.com",
        "given_name": "Test",
        "family_name": "User",
        "roles": ["user"],
        "aud": "test-client-id",
        "iss": "https://test-sso.example.com",
        "iat": now - 7200,  # 2 hours ago
        "exp": now - 3600,  # 1 hour ago
    }


@pytest.fixture
def jwt_payload_malformed():
    """Create a malformed JWT payload (missing email)."""
    now = int(time.time())
    return {
        "sub": "user123",
        # email is missing
        "given_name": "Test",
        "family_name": "User",
        "roles": ["user"],
        "aud": "test-client-id",
        "iss": "https://test-sso.example.com",
        "iat": now,
        "exp": now + 3600,
    }


@pytest.fixture
def jwt_payload_invalid_email():
    """Create a JWT payload with invalid email format."""
    now = int(time.time())
    return {
        "sub": "user123",
        "email": "not-an-email",
        "given_name": "Test",
        "family_name": "User",
        "roles": ["user"],
        "aud": "test-client-id",
        "iss": "https://test-sso.example.com",
        "iat": now,
        "exp": now + 3600,
    }


@pytest.fixture
def valid_token(jwt_payload_regular):
    """Create a valid JWT token."""
    # Use PyJWT for token generation
    return jwt.encode(jwt_payload_regular, RSA_PRIVATE_KEY, algorithm="RS256")


@pytest.fixture
def admin_token(jwt_payload_admin):
    """Create a valid JWT token for admin user."""
    # Use PyJWT for token generation
    return jwt.encode(jwt_payload_admin, RSA_PRIVATE_KEY, algorithm="RS256")


@pytest.fixture
def untrusted_admin_token(jwt_payload_admin_untrusted):
    """Create a valid JWT token for untrusted admin."""
    # Use PyJWT for token generation
    return jwt.encode(jwt_payload_admin_untrusted, RSA_PRIVATE_KEY, algorithm="RS256")


@pytest.fixture
def trusted_domain_token(jwt_payload_trusted_domain):
    """Create a valid JWT token for trusted domain user."""
    # Use PyJWT for token generation
    return jwt.encode(jwt_payload_trusted_domain, RSA_PRIVATE_KEY, algorithm="RS256")


@pytest.fixture
def expired_token(jwt_payload_expired):
    """Create an expired JWT token."""
    # Use PyJWT for token generation
    return jwt.encode(jwt_payload_expired, RSA_PRIVATE_KEY, algorithm="RS256")


@pytest.fixture
def malformed_token(jwt_payload_malformed):
    """Create a malformed JWT token (missing email)."""
    # Use PyJWT for token generation
    return jwt.encode(jwt_payload_malformed, RSA_PRIVATE_KEY, algorithm="RS256")


@pytest.fixture
def invalid_email_token(jwt_payload_invalid_email):
    """Create a JWT token with invalid email format."""
    # Use PyJWT for token generation
    return jwt.encode(jwt_payload_invalid_email, RSA_PRIVATE_KEY, algorithm="RS256")


@pytest.fixture
def mock_response():
    """Create a mock response for requests."""
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = {
        "email": "user@example.com",
        "first_name": "Test",
        "last_name": "User",
        "roles": ["user"],
    }
    return mock


@pytest.fixture
def mock_admin_response():
    """Create a mock response for admin user."""
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = {
        "email": "admin@example.com",
        "first_name": "Admin",
        "last_name": "User",
        "roles": ["user", "admin"],
    }
    return mock
