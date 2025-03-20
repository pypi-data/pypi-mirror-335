# Organization Unified Access Authentication

A Django authentication middleware package for integrating with OrganizationUnifiedAccess (OUA) SSO server.

## Installation

```bash
pip install oua-auth
```

## Configuration

Add the following settings to your Django settings.py:

```python
# OUA SSO Settings
OUA_SSO_URL = 'https://your-sso-server.com'  # Your OUA SSO server URL
OUA_PUBLIC_KEY = '''
-----BEGIN PUBLIC KEY-----
Your SSO public key here
-----END PUBLIC KEY-----
'''
OUA_CLIENT_ID = 'your-client-id'  # Your client ID from OUA SSO

# Optional: Paths to exclude from authentication
OUA_EXCLUDE_PATHS = [
    '/public/',
    '/api/health/',
]

# Security settings (recommended)
OUA_TRUSTED_ADMIN_DOMAINS = ['yourdomain.com']  # Domains allowed admin access
OUA_TRUSTED_ADMIN_EMAILS = ['admin@example.com']  # Specific emails allowed admin access
OUA_TOKEN_SIGNING_KEY = 'your-separate-signing-key'  # For internal token generation
OUA_INTERNAL_TOKEN_LIFETIME = 3600  # 1 hour in seconds
OUA_REQUEST_TIMEOUT = 5  # Timeout for SSO requests in seconds
OUA_MAX_REQUESTS_PER_MINUTE = 60  # Rate limiting for SSO API requests
OUA_MAX_AUTH_FAILURES = 5  # Maximum number of authentication failures before rate limiting
OUA_AUTH_FAILURE_WINDOW = 300  # Time window for rate limiting (seconds)

# Rate limiting cache configuration (optional)
OUA_RATELIMIT_CACHE_PREFIX = "oua_auth_failure"  # Prefix for cache keys
OUA_RATELIMIT_CACHE_TIMEOUT = 300  # Cache timeout for rate limit entries (seconds)

# User validation options (optional)
OUA_ALLOWED_DOMAINS = ['company.com', 'partner.org']  # Only these domains are allowed
OUA_RESTRICTED_DOMAINS = ['competitor.com', 'spam.org']  # These domains are blocked
OUA_REQUIRED_TOKEN_ATTRIBUTES = ['email', 'name', 'sub']  # Token must include these attributes

# Account locking (optional)
OUA_MAX_SUSPICIOUS_ACTIVITIES = 3  # Number of suspicious activities before account lock
OUA_SUSPICIOUS_ACTIVITY_WINDOW = 86400  # Time window for counting suspicious activities (seconds)
OUA_ACCOUNT_LOCK_DURATION = 86400  # How long accounts remain locked (seconds)
OUA_SUSPICIOUS_ACTIVITY_TYPES = [  # Activity types that count toward locking
    'token_reuse',
    'invalid_origin',
    'unusual_location',
    'multiple_failed_attempts'
]

# Add the authentication backend
AUTHENTICATION_BACKENDS = [
    'oua_auth.OUAAuthBackend',
    'django.contrib.auth.backends.ModelBackend',  # Optional: Keep Django's default backend
]

# Add the middleware
MIDDLEWARE = [
    # ... other middleware ...
    'oua_auth.OUAAuthMiddleware',
    'oua_auth.OUAUserMiddleware',  # Optional: For user data sync
    'oua_auth.SecurityHeadersMiddleware',  # Optional: For security headers
]

# If using Django Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'oua_auth.OUAJWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # Optional
    ],
    # ... other DRF settings
}
```

## Usage

### Authentication Flow

1. Your frontend obtains a JWT token from the OUA SSO server
2. Include the token in the Authorization header for API requests:
   ```
   Authorization: Bearer <your-jwt-token>
   ```
3. The middleware will:
   - Validate the JWT token
   - Create/update the Django user based on the token claims
   - Set request.user to the authenticated user
   - Store the token and claims in request.oua_token and request.oua_claims
   - Generate an internal token for added security

### Protecting Views

Use Django's standard authentication decorators:

```python
from django.contrib.auth.decorators import login_required

@login_required
def protected_view(request):
    # Only authenticated users can access this view
    return HttpResponse("Hello " + request.user.email)
```

For class-based views:

```python
from django.contrib.auth.mixins import LoginRequiredMixin

class ProtectedView(LoginRequiredMixin, View):
    def get(self, request):
        return HttpResponse("Hello " + request.user.email)
```

### Accessing Token Claims

The middleware stores the decoded JWT claims in the request:

```python
def my_view(request):
    if request.user.is_authenticated:
        roles = request.oua_claims.get('roles', [])
        if 'admin' in roles:
            # Handle admin user
            pass
```

### Using the Internal Token

For extra security, you can use the internal token for downstream services:

```python
def api_call(request):
    if request.user.is_authenticated:
        # Use the internal token for internal service calls
        internal_token = request.internal_token
        response = requests.get(
            'https://your-internal-service.com/api/resource',
            headers={"Authorization": f"Bearer {internal_token}"},
        )
        return JsonResponse(response.json())
```

### Token Blacklisting

This package includes persistent token blacklisting to revoke access for specific tokens:

```python
from oua_auth import OUAJWTAuthentication

def logout_user(request):
    """Revoke the current user's token and log them out."""
    if hasattr(request, 'oua_token'):
        # Blacklist the token
        OUAJWTAuthentication.revoke_token(
            token=request.oua_token,
            blacklisted_by=request.user.email,
            reason="User logout"
        )

    # Continue with standard Django logout
    from django.contrib.auth import logout
    logout(request)
    return redirect('login')

def admin_revoke_token(request, user_id, token_id):
    """Admin functionality to revoke a specific user's token."""
    if not request.user.is_staff:
        return HttpResponseForbidden()

    # Get the token from your token storage
    token = get_token_by_id(token_id)

    # Blacklist it
    OUAJWTAuthentication.revoke_token(
        token=token,
        blacklisted_by=f"Admin: {request.user.email}",
        reason=f"Admin revocation for user {user_id}"
    )

    return JsonResponse({"status": "success"})
```

The token blacklist is stored in the database using the `BlacklistedToken` model. Make sure to include `oua_auth` in your `INSTALLED_APPS` setting:

```python
INSTALLED_APPS = [
    # ... other apps ...
    'oua_auth',
    # ... other apps ...
]
```

After adding the app, run migrations to create the token blacklist table:

```bash
python manage.py migrate oua_auth
```

The blacklist automatically cleans up expired tokens during validation checks to prevent database growth. You can also set up a periodic task to clean expired tokens:

```python
from django.core.management.base import BaseCommand
from oua_auth.models import BlacklistedToken

class Command(BaseCommand):
    help = 'Clean expired tokens from the blacklist'

    def handle(self, *args, **options):
        count = BlacklistedToken.clean_expired_tokens()
        self.stdout.write(self.style.SUCCESS(f'Removed {count} expired tokens from blacklist'))
```

### Security Headers Middleware

The package includes a security headers middleware that adds recommended HTTP security headers to all responses:

```python
# Add the middleware to your MIDDLEWARE setting
MIDDLEWARE = [
    # ... other middleware ...
    'oua_auth.SecurityHeadersMiddleware',
]

# Optional: Configure security headers (these are the defaults)
OUA_CONTENT_SECURITY_POLICY = "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'"
OUA_FRAME_OPTIONS = "SAMEORIGIN"  # X-Frame-Options
OUA_XSS_PROTECTION = "1; mode=block"  # X-XSS-Protection
OUA_CONTENT_TYPE_OPTIONS = "nosniff"  # X-Content-Type-Options
OUA_REFERRER_POLICY = "strict-origin-when-cross-origin"
OUA_PERMISSIONS_POLICY = "geolocation=(), microphone=(), camera=(), payment=()"

# HSTS is disabled by default; enable and configure if your site uses HTTPS
OUA_ENABLE_HSTS = False  # Set to True to enable HSTS
OUA_HSTS_SECONDS = 31536000  # 1 year
OUA_HSTS_INCLUDE_SUBDOMAINS = True
OUA_HSTS_PRELOAD = False

# Exclude paths from security headers (optional)
OUA_SECURITY_HEADERS_EXCLUDE_PATHS = ['/api/public/', '/healthcheck/']
```

This middleware helps protect against common web vulnerabilities:

- **Content Security Policy (CSP)**: Controls what resources can be loaded
- **X-Frame-Options**: Protects against clickjacking
- **X-XSS-Protection**: Enables browser's XSS filtering
- **X-Content-Type-Options**: Prevents MIME-type sniffing
- **Referrer-Policy**: Controls what information is sent in the Referer header
- **Permissions-Policy**: Restricts which browser features can be used
- **HTTP Strict Transport Security (HSTS)**: Forces secure connections

## Security Features

This package implements several security measures:

- **JWT Token Security**: RSA256 signature verification, expiration validation
- **Privilege Protection**: Admin roles only granted to trusted email domains/addresses
- **Input Validation**:
  - Email format validation
  - XSS protection using the `bleach` library to sanitize all user inputs
  - HTML tag stripping and attribute filtering
  - Input length limitations to prevent DoS attacks
- **Network Security**: HTTPS enforcement, connection pooling, timeout controls
- **Internal Tokens**: Separate signing key, unique token IDs, expiration control
- **Distributed Rate Limiting**:
  - Cache-based tracking of authentication failures
  - IP-based rate limiting that works across multiple servers/instances
  - Configurable thresholds and time windows
  - Automatic cleanup of old failure records
- **Token Blacklisting**: Persistent revocation of compromised tokens
- **Security Headers**: Protection against XSS, CSRF, clickjacking and other web vulnerabilities
- **Structured Logging**: Sanitized logging with sensitive data redaction
- **User Validation Rules**:
  - Domain allowlisting and blocklisting for all users (not just admins)
  - Required token attributes validation
  - Automatic account locking after suspicious activity
- **Suspicious Activity Monitoring**:
  - Tracking and logging of suspicious authentication activities
  - Automatic account locking based on configurable thresholds
  - Protection against brute force, token reuse, and unusual access patterns

See [SECURITY.md](SECURITY.md) for more details on security features and vulnerability reporting.

### User Validation and Security Configuration

The package includes enhanced user validation to control access and detect potentially malicious activities:

```python
# Domain Restrictions (Optional)
OUA_ALLOWED_DOMAINS = ['company.com', 'partner.org']  # Only these domains can access
OUA_RESTRICTED_DOMAINS = ['competitor.com']  # These domains are blocked

# Token Attribute Requirements (Optional)
OUA_REQUIRED_TOKEN_ATTRIBUTES = ['email', 'name', 'sub', 'groups']

# Account Locking Configuration
OUA_MAX_SUSPICIOUS_ACTIVITIES = 3  # Activities before locking
OUA_SUSPICIOUS_ACTIVITY_WINDOW = 86400  # 24 hour window
OUA_ACCOUNT_LOCK_DURATION = 86400  # Lock for 24 hours
```

These features provide several important security benefits:

1. **Domain Control**: Limit access to specific trusted domains or block known malicious domains
2. **Token Validation**: Ensure tokens contain all required claims for your application's needs
3. **Suspicious Activity Detection**: Identify and respond to unusual authentication patterns
4. **Account Protection**: Automatically lock accounts when suspicious behavior is detected
5. **Audit Trail**: Track all security events for compliance and forensic analysis

All security events are logged in a structured format and can be reviewed in the Django admin interface or forwarded to security information and event management (SIEM) systems.

### Rate Limiting Configuration

The package includes a distributed rate limiting system that uses Django's cache framework to prevent brute force attacks:

```python
# Rate Limiting Configuration (add to your settings.py)
OUA_MAX_AUTH_FAILURES = 5       # Maximum authentication failures before rate limiting
OUA_AUTH_FAILURE_WINDOW = 300   # Time window for counting failures (seconds)

# Cache backend settings (optional)
OUA_RATELIMIT_CACHE_PREFIX = "oua_auth_failure"  # Prefix for cache keys
OUA_RATELIMIT_CACHE_TIMEOUT = 300  # Cache entry timeout (seconds)
```

For optimal security in production environments, configure Django's cache framework with a distributed backend:

```python
# Example: Redis cache backend (requires django-redis)
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Example: Memcached backend
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
```

The rate limiting system:

- Tracks authentication failures by client IP address
- Blocks access after too many failed attempts
- Works across multiple server instances
- Automatically expires old failure records
- Provides detailed logging for security monitoring

### Structured Logging Configuration

The package includes a comprehensive logging system with structured log output and sensitive data redaction:

```python
# Logging Configuration (add to your settings.py)
OUA_LOG_LEVEL = "INFO"  # Global log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
OUA_CONSOLE_LOG_LEVEL = "INFO"  # Console-specific log level
OUA_FILE_LOG_LEVEL = "DEBUG"  # File-specific log level
OUA_LOG_FILE = "/var/log/django/oua_auth.log"  # Log file path (None for no file logging)
OUA_LOG_JSON = True  # Output logs in JSON format for log aggregation systems
OUA_LOG_CONSOLE = True  # Output logs to console
OUA_EAGER_LOGGING = False  # Configure logging during import (vs. Django app initialization)
```

The logging system provides:

- **Structured JSON Output**: For better integration with log management systems like ELK, Splunk, or Graylog
- **Sensitive Data Redaction**: Automatically redacts tokens, passwords and other sensitive information
- **Contextual Information**: Includes request IDs, user information, and process details for easier debugging
- **Configurable Verbosity**: Control log level globally or per output channel
- **File Rotation**: Automatically rotates log files to prevent disk space issues

You can use the built-in logging utilities in your own code:

```python
from oua_auth import setup_logging

# Create a logger for your module
logger = setup_logging(__name__)

# Log with context data
logger.info("User action completed", extra={"user_id": user.id, "action": "login"})

# Create a logger with default context
user_logger = logger.with_context(user_id=user.id, user_email=user.email)
user_logger.info("Profile updated")  # Will include user context automatically

# Use decorator to log requests (with timing)
from oua_auth import log_request

@log_request()
def my_view(request):
    # Request start and end will be logged automatically with timing
    return HttpResponse("Hello World")
```

The structured logs include consistent fields that make it easy to filter and analyze:

- **level**: Log level (INFO, WARNING, ERROR, etc.)
- **time**: ISO-8601 timestamp with timezone
- **message**: The log message
- **module**: Source module name
- **function**: Source function name
- **line**: Source line number
- **request_id**: Unique identifier for the request (for correlation)
- **user_id**: User ID if available
- **ip_address**: Client IP address if available
- **component**: Component name (e.g., "authentication", "middleware")
- **extra**: Additional context-specific information

## Features

- JWT token validation
- Automatic user creation and updates
- Role-based authorization with security controls
- User data synchronization with SSO server
- Path-based authentication exclusion
- Django admin integration
- Django Rest Framework support

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Testing

The package includes a comprehensive test suite to ensure its functionality and security:

```bash
# Install test dependencies
pip install -e ".[test]"

# Run the test suite
python -m pytest

# Run tests with coverage report
python -m pytest --cov=oua_auth --cov-report=term-missing
```

The test suite covers:

- JWT token validation and verification
- User creation and updates
- Admin privilege management
- Error handling
- Security features

See [tests/README.md](tests/README.md) for more details on the test suite.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
