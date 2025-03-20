# Configuration Guide for OUA Authentication

This document provides comprehensive information about all configuration options available in the Organization Unified Access Authentication (OUA Auth) system.

## Core Configuration

These are essential configuration options required for the OUA Authentication system to function properly.

### Required Settings

| Setting          | Description                                                   | Default         | Example                                             |
| ---------------- | ------------------------------------------------------------- | --------------- | --------------------------------------------------- |
| `OUA_SSO_URL`    | The URL of your OUA SSO server. Must use HTTPS in production. | None (Required) | `'https://sso.example.com'`                         |
| `OUA_PUBLIC_KEY` | The RSA public key used to verify JWT tokens.                 | None (Required) | Multi-line string with BEGIN/END PUBLIC KEY markers |
| `OUA_CLIENT_ID`  | Your application's client ID registered with the SSO server.  | None (Required) | `'your-client-id'`                                  |

### Middleware Configuration

Add these middleware classes to your Django `MIDDLEWARE` setting:

```python
MIDDLEWARE = [
    # Add Django's security middleware first
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    # OUA Auth middleware
    'oua_auth.OUAAuthMiddleware',  # Required for authentication
    'oua_auth.OUAUserMiddleware',  # Optional: For user data synchronization
    'oua_auth.SecurityHeadersMiddleware',  # Optional: For security headers

    # Other middleware
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

### Authentication Backends

Add the OUA Auth backend to your `AUTHENTICATION_BACKENDS` setting:

```python
AUTHENTICATION_BACKENDS = [
    'oua_auth.OUAAuthBackend',
    'django.contrib.auth.backends.ModelBackend',  # Optional: Keep Django's default backend
]
```

### Django Rest Framework Integration

If you're using Django Rest Framework, add the OUA JWT Authentication class:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'oua_auth.OUAJWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # Optional
    ],
    # ... other DRF settings
}
```

### Database Configuration

Add `oua_auth` to your `INSTALLED_APPS` setting to enable models for token blacklisting and suspicious activity tracking:

```python
INSTALLED_APPS = [
    # ... other apps ...
    'oua_auth',
    # ... other apps ...
]
```

After adding the app, run migrations:

```bash
python manage.py migrate oua_auth
```

## Access Control Configuration

These settings control who can access your application and with what level of privileges.

### Path Exclusion

Specify paths that should be accessible without authentication:

```python
# Optional: Paths to exclude from authentication
OUA_EXCLUDE_PATHS = [
    '/public/',
    '/api/health/',
    '/static/',
    '/media/',
]
```

### Domain Restrictions

Control which email domains are allowed to access your application:

```python
# Allow only these domains (if empty, all domains are allowed)
OUA_ALLOWED_DOMAINS = ['company.com', 'partner.org']

# Block these domains
OUA_RESTRICTED_DOMAINS = ['competitor.com', 'spam.org']
```

### Admin Access Controls

Specify which domains and email addresses are allowed admin privileges:

```python
# Domains allowed admin access
OUA_TRUSTED_ADMIN_DOMAINS = ['admin.company.com', 'internal.company.com']

# Specific emails allowed admin access
OUA_TRUSTED_ADMIN_EMAILS = ['admin@company.com', 'superuser@company.com']
```

### Required Token Attributes

Specify which attributes must be present in JWT tokens:

```python
# Token must include these attributes
OUA_REQUIRED_TOKEN_ATTRIBUTES = ['email', 'name', 'sub', 'groups']
```

## Security Configuration

These settings control various security features of the OUA Authentication system.

### Token Settings

Configure how tokens are generated and validated:

```python
# For internal token generation
OUA_TOKEN_SIGNING_KEY = 'your-secure-signing-key'

# Internal token lifetime in seconds (1 hour default)
OUA_INTERNAL_TOKEN_LIFETIME = 3600

# Timeout for SSO requests in seconds
OUA_REQUEST_TIMEOUT = 5
```

### Rate Limiting

Configure rate limiting to prevent brute force attacks:

```python
# Maximum requests per minute to the SSO server
OUA_MAX_REQUESTS_PER_MINUTE = 60

# Maximum number of authentication failures before rate limiting
OUA_MAX_AUTH_FAILURES = 5

# Time window for rate limiting in seconds
OUA_AUTH_FAILURE_WINDOW = 300

# Cache settings for rate limiting
OUA_RATELIMIT_CACHE_PREFIX = "oua_auth_failure"
OUA_RATELIMIT_CACHE_TIMEOUT = 300
```

### Suspicious Activity Detection

Configure how suspicious activities are detected and handled:

```python
# Number of suspicious activities before account lock
OUA_MAX_SUSPICIOUS_ACTIVITIES = 3

# Time window for counting suspicious activities (24 hours in seconds)
OUA_SUSPICIOUS_ACTIVITY_WINDOW = 86400

# How long accounts remain locked (24 hours in seconds)
OUA_ACCOUNT_LOCK_DURATION = 86400

# Activity types that count toward locking
OUA_SUSPICIOUS_ACTIVITY_TYPES = [
    'token_reuse',
    'invalid_origin',
    'unusual_location',
    'multiple_failed_attempts'
]
```

### Security Headers

Configure security headers added by the `SecurityHeadersMiddleware`:

```python
# Content Security Policy
OUA_CONTENT_SECURITY_POLICY = "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'"

# X-Frame-Options
OUA_FRAME_OPTIONS = "SAMEORIGIN"

# X-XSS-Protection
OUA_XSS_PROTECTION = "1; mode=block"

# X-Content-Type-Options
OUA_CONTENT_TYPE_OPTIONS = "nosniff"

# Referrer-Policy
OUA_REFERRER_POLICY = "strict-origin-when-cross-origin"

# Permissions-Policy
OUA_PERMISSIONS_POLICY = "geolocation=(), microphone=(), camera=(), payment=()"

# HTTP Strict Transport Security (HSTS)
OUA_ENABLE_HSTS = True  # Set to True in production
OUA_HSTS_SECONDS = 31536000  # 1 year
OUA_HSTS_INCLUDE_SUBDOMAINS = True
OUA_HSTS_PRELOAD = False

# Exclude paths from security headers
OUA_SECURITY_HEADERS_EXCLUDE_PATHS = ['/api/public/', '/healthcheck/']
```

## Logging Configuration

Configure logging for the OUA Authentication system:

```python
# Django Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'json': {
            '()': 'oua_auth.logging_utils.JSONFormatter',
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/path/to/your/auth.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'json',
        },
    },
    'loggers': {
        'oua_auth': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Advanced logging configuration
OUA_REDACT_SENSITIVE_DATA = True  # Redact tokens, passwords in logs
OUA_LOG_REQUEST_BODIES = False  # Whether to log request bodies (potential security risk)
OUA_LOG_RESPONSE_BODIES = False  # Whether to log response bodies
OUA_LOG_HEADERS = ['User-Agent', 'Referer']  # Headers to include in logs
```

## Cache Configuration

The OUA Authentication system uses Django's cache framework for rate limiting and other features. Configure it according to your needs:

```python
# Simple local memory cache (for development)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Redis cache (recommended for production)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

## Advanced Configuration

These settings are for advanced use cases and fine-tuning.

### Token Validation

```python
# Additional token validation options
OUA_VERIFY_TOKEN_EXPIRATION = True  # Whether to check token expiration
OUA_VERIFY_TOKEN_ISSUER = True  # Whether to verify token issuer
OUA_ALLOWED_TOKEN_ISSUERS = ['https://sso.company.com']  # Allowed issuers
OUA_TOKEN_LEEWAY = 10  # Seconds of leeway for token expiration checks
```

### User Creation and Mapping

```python
# User field mapping from token claims to User model fields
OUA_USER_FIELD_MAPPINGS = {
    'email': 'email',
    'given_name': 'first_name',
    'family_name': 'last_name',
    'preferred_username': 'username',
}

# Whether to create users automatically if they don't exist
OUA_CREATE_USERS = True

# Whether to update existing users with information from token
OUA_UPDATE_USERS = True

# Field for storing user roles/groups from token
OUA_USER_ROLES_FIELD = 'roles'
```

### Performance Tuning

```python
# Cache lifetime for validated tokens (in seconds)
OUA_TOKEN_CACHE_LIFETIME = 60

# Maximum token size in bytes (to prevent DoS attacks)
OUA_MAX_TOKEN_SIZE = 8192

# Maximum header size in bytes
OUA_MAX_HEADER_SIZE = 16384
```

## Environment Variables

For better security, many of these settings can be provided via environment variables instead of hardcoding them in your settings file:

```python
import os

OUA_SSO_URL = os.environ.get('OUA_SSO_URL')
OUA_PUBLIC_KEY = os.environ.get('OUA_PUBLIC_KEY')
OUA_CLIENT_ID = os.environ.get('OUA_CLIENT_ID')
OUA_TOKEN_SIGNING_KEY = os.environ.get('OUA_TOKEN_SIGNING_KEY')
```

## Configuration Templates

### Minimal Configuration

```python
# Minimal OUA Auth configuration
OUA_SSO_URL = 'https://sso.example.com'
OUA_PUBLIC_KEY = '''
-----BEGIN PUBLIC KEY-----
...your public key here...
-----END PUBLIC KEY-----
'''
OUA_CLIENT_ID = 'your-client-id'

MIDDLEWARE = [
    # ... other middleware ...
    'oua_auth.OUAAuthMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'oua_auth.OUAAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]

INSTALLED_APPS = [
    # ... other apps ...
    'oua_auth',
]
```

### Recommended Production Configuration

```python
# Recommended production configuration
OUA_SSO_URL = 'https://sso.example.com'
OUA_PUBLIC_KEY = '''
-----BEGIN PUBLIC KEY-----
...your public key here...
-----END PUBLIC KEY-----
'''
OUA_CLIENT_ID = 'your-client-id'
OUA_TOKEN_SIGNING_KEY = 'your-secure-signing-key'

# Security settings
OUA_TRUSTED_ADMIN_DOMAINS = ['admin.company.com']
OUA_MAX_AUTH_FAILURES = 5
OUA_AUTH_FAILURE_WINDOW = 300
OUA_MAX_SUSPICIOUS_ACTIVITIES = 3
OUA_ACCOUNT_LOCK_DURATION = 86400
OUA_ENABLE_HSTS = True

# Middlewares
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # ... other middleware ...
    'oua_auth.OUAAuthMiddleware',
    'oua_auth.OUAUserMiddleware',
    'oua_auth.SecurityHeadersMiddleware',
]

# Authentication
AUTHENTICATION_BACKENDS = [
    'oua_auth.OUAAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'oua_auth.OUAJWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
}

# Cache (Redis recommended for production)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
    }
}

INSTALLED_APPS = [
    # ... other apps ...
    'oua_auth',
]
```
