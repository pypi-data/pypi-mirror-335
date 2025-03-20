# Troubleshooting Guide for OUA Authentication

This guide provides solutions for common issues you might encounter when working with the Organization Unified Access Authentication (OUA Auth) system. Follow these steps to diagnose and resolve problems.

## General Troubleshooting Steps

When you encounter an issue with OUA Auth, follow these general troubleshooting steps:

1. **Check logs**: Look for error messages in your application logs
2. **Verify configuration**: Double-check your OUA Auth settings in `settings.py`
3. **Validate token**: Use a tool like [JWT.io](https://jwt.io/) to inspect your token (in development only)
4. **Check network requests**: Use browser developer tools or a tool like Postman to inspect request/response details

## Authentication Failures

### Token Validation Issues

#### Symptom: "Signature verification failed" error

**Possible causes:**

- Incorrect public key
- Token not signed with the corresponding private key
- Token tampering

**Solutions:**

1. Verify that your `OUA_PUBLIC_KEY` setting contains the correct public key
2. Ensure the public key includes proper BEGIN/END markers:
   ```
   -----BEGIN PUBLIC KEY-----
   ...public key content...
   -----END PUBLIC KEY-----
   ```
3. Check that the token was signed by the expected SSO server
4. Try regenerating the token from your SSO server

#### Symptom: "Token has expired" error

**Possible causes:**

- The token has passed its expiration time
- Clock skew between servers

**Solutions:**

1. Request a new token from your SSO server
2. If clock skew is the issue, you can add some leeway to token validation:
   ```python
   # In settings.py
   OUA_TOKEN_LEEWAY = 60  # 60 seconds of leeway
   ```
3. Synchronize the clocks on your servers using NTP

#### Symptom: "Invalid token" or "Invalid claim" error

**Possible causes:**

- Missing required claims in the token
- Token format issues
- Token doesn't match expected audience

**Solutions:**

1. Check that your SSO server includes all required claims in the token
2. Verify the token format is correct
3. Ensure the `aud` claim in the token matches your `OUA_CLIENT_ID`
4. Check for proper encoding of special characters in claims

### Token Blacklist Issues

#### Symptom: Valid token rejected with "Token has been blacklisted" message

**Possible causes:**

- Token was explicitly blacklisted
- Database query issues

**Solutions:**

1. Check the `BlacklistedToken` model in the admin interface
2. Look for entries matching your token's hash
3. Clear specific entries if needed:

   ```python
   from oua_auth.models import BlacklistedToken

   # Find and delete specific entries
   token_hash = hashlib.sha256("your-token-here".encode()).hexdigest()
   BlacklistedToken.objects.filter(token_hash=token_hash).delete()
   ```

#### Symptom: Blacklisted tokens are still being accepted

**Possible causes:**

- Database replication lag
- Cache inconsistency
- Missing database migrations

**Solutions:**

1. Check that you've run migrations for the `oua_auth` app:
   ```bash
   python manage.py migrate oua_auth
   ```
2. Ensure your database connection is working correctly
3. Clear your cache:
   ```python
   from django.core.cache import cache
   cache.clear()
   ```
4. Check database replication status if using replicated databases

### Rate Limiting Issues

#### Symptom: "Rate limit exceeded" error

**Possible causes:**

- Too many authentication attempts in a short period
- Cache configuration issues

**Solutions:**

1. Wait for the rate limit window to expire (usually 5-15 minutes)
2. Adjust rate limiting settings if needed:
   ```python
   # In settings.py
   OUA_MAX_AUTH_FAILURES = 10  # Increase from default
   OUA_AUTH_FAILURE_WINDOW = 600  # Extend window to 10 minutes
   ```
3. Verify your cache is working correctly:

   ```python
   from django.core.cache import cache

   # Test cache
   cache.set('test_key', 'test_value', 60)
   assert cache.get('test_key') == 'test_value'
   ```

#### Symptom: Rate limiting not working

**Possible causes:**

- Cache not configured properly
- Cache server not running
- Incorrect cache backend

**Solutions:**

1. Check your cache configuration:
   ```python
   # In settings.py
   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.redis.RedisCache',
           'LOCATION': 'redis://redis:6379/1',
       }
   }
   ```
2. Ensure your cache server is running
3. Test connection to cache server:
   ```bash
   redis-cli ping  # Should return PONG
   ```

## User Authentication Issues

### User Creation Problems

#### Symptom: Users not being created automatically

**Possible causes:**

- Missing setting for automatic user creation
- Token missing user information
- Database permission issues

**Solutions:**

1. Check that automatic user creation is enabled:
   ```python
   # In settings.py
   OUA_CREATE_USERS = True
   ```
2. Verify token contains required user information (email at minimum)
3. Check database permissions for Django user creation
4. Look for database errors in logs

#### Symptom: Users created but missing data

**Possible causes:**

- Token missing expected claims
- Field mapping issues

**Solutions:**

1. Check the token content to ensure it has the expected claims
2. Verify field mappings:
   ```python
   # In settings.py
   OUA_USER_FIELD_MAPPINGS = {
       'email': 'email',
       'given_name': 'first_name',
       'family_name': 'last_name',
       'preferred_username': 'username',
   }
   ```
3. Ensure your Django user model has the expected fields

### Admin Access Issues

#### Symptom: Admin users not getting admin privileges

**Possible causes:**

- Admin domain configuration issues
- Token missing role/group information
- Admin detection failing

**Solutions:**

1. Check admin domain settings:
   ```python
   # In settings.py
   OUA_TRUSTED_ADMIN_DOMAINS = ['admin.company.com']
   OUA_TRUSTED_ADMIN_EMAILS = ['admin@company.com']
   ```
2. Verify token includes expected admin role or group claims
3. Ensure your middleware order is correct:
   ```python
   MIDDLEWARE = [
       # ... other middleware ...
       'django.contrib.auth.middleware.AuthenticationMiddleware',
       'oua_auth.OUAAuthMiddleware',
       'oua_auth.OUAUserMiddleware',
       # ... other middleware ...
   ]
   ```

## Integration Issues

### Django REST Framework Issues

#### Symptom: Token not being recognized by DRF views

**Possible causes:**

- Authentication class not configured correctly
- Middleware order issues

**Solutions:**

1. Check DRF authentication classes:
   ```python
   # In settings.py
   REST_FRAMEWORK = {
       'DEFAULT_AUTHENTICATION_CLASSES': [
           'oua_auth.OUAJWTAuthentication',
           'rest_framework.authentication.SessionAuthentication',
       ],
   }
   ```
2. Verify middleware order:
   ```python
   MIDDLEWARE = [
       # ... other middleware ...
       'django.contrib.auth.middleware.AuthenticationMiddleware',  # Must be before OUA middleware
       'oua_auth.OUAAuthMiddleware',
       # ... other middleware ...
   ]
   ```
3. Check token in request headers:
   ```
   Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

### CORS Issues

#### Symptom: Browser shows CORS errors

**Possible causes:**

- CORS middleware not installed or configured
- Missing allowed origins
- Middleware order incorrect

**Solutions:**

1. Install django-cors-headers:
   ```bash
   pip install django-cors-headers
   ```
2. Add to installed apps:
   ```python
   INSTALLED_APPS = [
       # ... other apps ...
       'corsheaders',
   ]
   ```
3. Add middleware in the correct position:
   ```python
   MIDDLEWARE = [
       'corsheaders.middleware.CorsMiddleware',  # Must be at or near the top
       # ... other middleware ...
   ]
   ```
4. Configure allowed origins:
   ```python
   CORS_ALLOWED_ORIGINS = [
       "https://example.com",
       "https://sub.example.com",
   ]
   ```
5. For development, you can allow all origins (not recommended for production):
   ```python
   CORS_ALLOW_ALL_ORIGINS = True  # Use only in development
   ```

### Frontend Integration Issues

#### Symptom: Frontend authentication not working

**Possible causes:**

- Token storage issues
- Token not included in requests
- CORS issues

**Solutions:**

1. Check token storage in frontend:

   ```javascript
   // Store token
   localStorage.setItem("auth_token", token);

   // Verify token exists
   const token = localStorage.getItem("auth_token");
   console.log("Token exists:", !!token);
   ```

2. Ensure token is included in API requests:
   ```javascript
   axios.get("/api/endpoint", {
     headers: {
       Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
     },
   });
   ```
3. Add request/response interceptors to automatically add the token:
   ```javascript
   axios.interceptors.request.use((config) => {
     const token = localStorage.getItem("auth_token");
     if (token) {
       config.headers.Authorization = `Bearer ${token}`;
     }
     return config;
   });
   ```

## Logging and Debugging

### Enabling Debug Logging

To get more detailed information about authentication issues:

```python
# In settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/path/to/auth_debug.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'oua_auth': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

### Common Log Messages and Solutions

#### Log: "Token validation failed: Token has expired"

**Solution:** Request a new token from your SSO server.

#### Log: "User not found and auto-creation disabled"

**Solution:** Enable user auto-creation:

```python
OUA_CREATE_USERS = True
```

#### Log: "Rate limit exceeded for IP x.x.x.x"

**Solution:** Wait for rate limit window to expire or adjust rate limiting settings.

#### Log: "Invalid email format in token"

**Solution:** Check that the token contains a properly formatted email claim.

#### Log: "Database unavailable for token blacklist check"

**Solution:** Check your database connection and ensure the `BlacklistedToken` model exists.

## Environment-Specific Issues

### Docker Deployment Issues

#### Symptom: Authentication works locally but fails in Docker

**Possible causes:**

- Environment variables not set correctly
- Network connectivity issues between containers
- Time synchronization issues

**Solutions:**

1. Check environment variables in Docker:
   ```yaml
   # docker-compose.yml
   services:
     web:
       environment:
         - OUA_SSO_URL=https://sso.example.com
         - OUA_CLIENT_ID=your-client-id
         # Public key needs special handling for multiline values
         - OUA_PUBLIC_KEY=-----BEGIN PUBLIC KEY-----\nMIIB...
   ```
2. Ensure network connectivity between containers:
   ```bash
   docker-compose exec web ping redis
   docker-compose exec web ping db
   ```
3. Synchronize time in containers:
   ```dockerfile
   # Dockerfile
   RUN apt-get update && apt-get install -y ntp
   ```

### Production vs Development Issues

#### Symptom: Authentication works in development but fails in production

**Possible causes:**

- Different configuration in production
- HTTPS/SSL issues
- Firewall or network restrictions

**Solutions:**

1. Compare your development and production settings
2. Check HTTPS configuration in production
3. Verify firewall rules allow necessary connections
4. Test token validation explicitly:

   ```python
   import jwt
   from django.conf import settings

   def test_token_validation(token):
       try:
           payload = jwt.decode(
               token,
               settings.OUA_PUBLIC_KEY,
               algorithms=['RS256'],
               audience=settings.OUA_CLIENT_ID
           )
           print("Token valid! Payload:", payload)
           return True
       except Exception as e:
           print("Token validation failed:", str(e))
           return False
   ```

## Database Related Issues

### Migration Issues

#### Symptom: "Table 'oua_auth_blacklistedtoken' doesn't exist" error

**Possible causes:**

- Migrations not applied
- Database connection issues

**Solutions:**

1. Apply migrations:
   ```bash
   python manage.py migrate oua_auth
   ```
2. Check migration status:
   ```bash
   python manage.py showmigrations oua_auth
   ```
3. If problems persist, try making migrations again:
   ```bash
   python manage.py makemigrations oua_auth
   python manage.py migrate oua_auth
   ```

### Database Performance Issues

#### Symptom: Authentication is slow

**Possible causes:**

- Inefficient database queries
- Missing indexes
- Database connection issues

**Solutions:**

1. Add indexes to frequently queried fields:
   ```python
   class Meta:
       indexes = [
           models.Index(fields=['email']),
       ]
   ```
2. Optimize database connections:
   ```python
   DATABASES = {
       'default': {
           # ... other settings ...
           'CONN_MAX_AGE': 600,  # Persistent connections
           'OPTIONS': {
               'connect_timeout': 5,
           }
       }
   }
   ```
3. Use connection pooling with pgbouncer or similar tools

## Command Line Diagnostics

These commands can help diagnose authentication issues:

### Check Token Blacklist

```bash
# Connect to Django shell
python manage.py shell

# In the shell
from oua_auth.models import BlacklistedToken
# Count blacklisted tokens
BlacklistedToken.objects.count()
# List recent entries
BlacklistedToken.objects.order_by('-created_at')[:5].values()
```

### Test Token Validation

```bash
# Connect to Django shell
python manage.py shell

# In the shell
from jose import jwt
from django.conf import settings

# Replace with your actual token
token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."

try:
    # Try to decode and validate the token
    payload = jwt.decode(
        token,
        settings.OUA_PUBLIC_KEY,
        algorithms=['RS256'],
        audience=settings.OUA_CLIENT_ID
    )
    print("Token is valid!")
    print("Payload:", payload)
except Exception as e:
    print("Token validation failed:", str(e))
```

### Check Cache Status

```bash
# Connect to Django shell
python manage.py shell

# In the shell
from django.core.cache import cache

# Test cache functionality
cache.set('test_key', 'test_value', 60)
value = cache.get('test_key')
print("Cache test:", value == 'test_value')

# Check rate limiting entries
prefix = "oua_auth_failure"
# You would need to know the exact key pattern based on your configuration
# This is just an example of what to look for
```

## Advanced Troubleshooting

### JWT Debugging Tools

For detailed JWT token inspection:

```python
def debug_token(token):
    """Print details about a JWT token without validation."""
    parts = token.split('.')
    if len(parts) != 3:
        return "Invalid token format"

    import base64
    import json

    # Decode header
    header_bytes = base64.urlsafe_b64decode(parts[0] + '=' * (4 - len(parts[0]) % 4))
    header = json.loads(header_bytes)

    # Decode payload
    payload_bytes = base64.urlsafe_b64decode(parts[1] + '=' * (4 - len(parts[1]) % 4))
    payload = json.loads(payload_bytes)

    return {
        "header": header,
        "payload": payload,
        "signature_exists": bool(parts[2])
    }
```

### Network Debugging

To debug network-related issues:

```bash
# Test SSO server connectivity
curl -v https://your-sso-server.com

# Test connectivity to other services
ping redis-server
ping database-server

# Check DNS resolution
nslookup your-sso-server.com
```

## Common Issues by Error Message

### "No authorization token provided"

**Possible causes:**

- Frontend not sending the token
- Middleware configuration issues

**Solutions:**

1. Check request headers in browser developer tools
2. Verify token is being sent correctly
3. Check middleware configuration

### "Token signature verification failed"

**Possible causes:**

- Incorrect public key
- Token tampered with
- Token signed with different algorithm

**Solutions:**

1. Verify public key is correct
2. Check token signature algorithm

### "User matching query does not exist"

**Possible causes:**

- Token contains email not in database
- User auto-creation disabled
- Database consistency issues

**Solutions:**

1. Enable user auto-creation:
   ```python
   OUA_CREATE_USERS = True
   ```
2. Check if user exists in database:
   ```python
   from django.contrib.auth import get_user_model
   User = get_user_model()
   User.objects.filter(email='user@example.com').exists()
   ```

## Recovering from Common Failures

### Reset Rate Limiting

To reset rate limiting for a specific IP or user:

```python
from django.core.cache import cache

# Reset for IP
ip_key = f"oua_auth_failure_ip_127.0.0.1"
cache.delete(ip_key)

# Reset for user
user_key = f"oua_auth_failure_user_user@example.com"
cache.delete(user_key)
```

### Unlock User Account

To unlock a user account that has been locked due to suspicious activity:

```python
from django.contrib.auth import get_user_model
User = get_user_model()

user = User.objects.get(email='user@example.com')
if hasattr(user, 'security_profile'):
    user.security_profile.unlock_account()
    print("Account unlocked successfully")
```

### Emergency Token Revocation

In case of a security incident, you may need to revoke all tokens:

```python
from oua_auth.models import BlacklistedToken
from django.utils import timezone
import uuid

# Create a wildcard entry (implementation depends on your specific system)
BlacklistedToken.add_token_to_blacklist(
    token=f"EMERGENCY_REVOCATION_{uuid.uuid4()}",
    blacklisted_by="security-team",
    reason="Security incident - emergency revocation",
    expires_at=timezone.now() + timezone.timedelta(days=365)
)

# Then modify your authentication code to check for this special entry
# This requires custom code in your application
```

## Getting Further Help

If you've tried these troubleshooting steps and still encounter issues:

1. **Check Issue Tracker**: Look for similar issues on the project's Gitlab repository
2. **Gather Diagnostic Information**:
   - Django version
   - OUA Auth version
   - Server environment details
   - Relevant log entries
   - Token examples (with sensitive data masked)
3. **Create Minimal Reproduction**: Create a minimal project that reproduces the issue

## Appendix: Health Check Script

A useful script to check the health of your OUA Auth installation:

```python
#!/usr/bin/env python
"""OUA Auth Health Check Script

Run this script to check the health of your OUA Auth installation.
"""

import os
import sys
import django
from django.conf import settings

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
django.setup()

def check_database():
    """Check database connection and models."""
    try:
        from oua_auth.models import BlacklistedToken
        count = BlacklistedToken.objects.count()
        print(f"✅ Database connection successful. Found {count} blacklisted tokens.")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def check_cache():
    """Check cache connection."""
    try:
        from django.core.cache import cache
        cache.set('oua_auth_healthcheck', 'working', 30)
        value = cache.get('oua_auth_healthcheck')
        if value == 'working':
            print("✅ Cache connection successful.")
            return True
        else:
            print(f"❌ Cache test failed. Expected 'working', got '{value}'.")
            return False
    except Exception as e:
        print(f"❌ Cache connection failed: {str(e)}")
        return False

def check_settings():
    """Check required settings."""
    required_settings = [
        'OUA_SSO_URL',
        'OUA_PUBLIC_KEY',
        'OUA_CLIENT_ID',
    ]

    all_good = True
    for setting_name in required_settings:
        if not hasattr(settings, setting_name):
            print(f"❌ Missing required setting: {setting_name}")
            all_good = False
        else:
            value = getattr(settings, setting_name)
            if value:
                print(f"✅ Setting {setting_name} found.")
            else:
                print(f"❌ Setting {setting_name} is empty.")
                all_good = False

    return all_good

def check_middleware():
    """Check middleware configuration."""
    required_middleware = [
        'oua_auth.OUAAuthMiddleware',
    ]

    all_good = True
    for middleware in required_middleware:
        if middleware in settings.MIDDLEWARE:
            print(f"✅ Required middleware found: {middleware}")
        else:
            print(f"❌ Missing required middleware: {middleware}")
            all_good = False

    # Check middleware order
    auth_middleware = 'django.contrib.auth.middleware.AuthenticationMiddleware'
    oua_middleware = 'oua_auth.OUAAuthMiddleware'

    if (auth_middleware in settings.MIDDLEWARE and
        oua_middleware in settings.MIDDLEWARE):
        auth_index = settings.MIDDLEWARE.index(auth_middleware)
        oua_index = settings.MIDDLEWARE.index(oua_middleware)

        if auth_index < oua_index:
            print("✅ Middleware order is correct.")
        else:
            print("❌ Middleware order is incorrect. AuthenticationMiddleware should come before OUAAuthMiddleware.")
            all_good = False

    return all_good

def main():
    """Run all health checks."""
    print("OUA Auth Health Check")
    print("===================")

    db_check = check_database()
    cache_check = check_cache()
    settings_check = check_settings()
    middleware_check = check_middleware()

    print("\nSummary:")
    print(f"Database: {'✅' if db_check else '❌'}")
    print(f"Cache: {'✅' if cache_check else '❌'}")
    print(f"Settings: {'✅' if settings_check else '❌'}")
    print(f"Middleware: {'✅' if middleware_check else '❌'}")

    if all([db_check, cache_check, settings_check, middleware_check]):
        print("\n✅ All checks passed. OUA Auth appears to be properly configured.")
        return 0
    else:
        print("\n❌ Some checks failed. Please address the issues listed above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

Save this as `oua_auth_healthcheck.py` and run it to check your installation:

```bash
python oua_auth_healthcheck.py
```
