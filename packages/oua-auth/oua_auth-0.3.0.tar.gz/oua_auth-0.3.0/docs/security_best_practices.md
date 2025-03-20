# Security Best Practices for OUA Authentication

This document outlines security best practices for deploying and operating the Organization Unified Access Authentication (OUA Auth) system. Following these guidelines will help ensure your authentication system remains secure and resilient against common attack vectors.

## Deployment Security

### HTTPS Everywhere

- **Always use HTTPS**: Never deploy the OUA Authentication system without HTTPS in production.
- **Configure HSTS**: Enable HTTP Strict Transport Security to enforce HTTPS connections:
  ```python
  OUA_ENABLE_HSTS = True
  OUA_HSTS_SECONDS = 31536000  # 1 year
  OUA_HSTS_INCLUDE_SUBDOMAINS = True
  ```
- **Consider HSTS Preloading**: For maximum security, consider enabling HSTS preloading:
  ```python
  OUA_HSTS_PRELOAD = True
  ```
  And submit your domain to the [HSTS Preload List](https://hstspreload.org/).

### Environment Configuration

- **Use Environment Variables**: Store sensitive configuration values as environment variables rather than in code:

  ```python
  import os

  OUA_PUBLIC_KEY = os.environ.get('OUA_PUBLIC_KEY')
  OUA_TOKEN_SIGNING_KEY = os.environ.get('OUA_TOKEN_SIGNING_KEY')
  ```

- **Use Secret Management**: For production, consider using a secret management solution like AWS Secrets Manager, HashiCorp Vault, or Django-Environ.
- **Restrict File Permissions**: Ensure configuration files with sensitive information have restricted permissions (e.g., 600).

### Infrastructure Security

- **Use a Web Application Firewall (WAF)**: Deploy behind a WAF to protect against common attacks.
- **Implement Network Segmentation**: Place authentication services in a separate security group or network segment.
- **Regular Security Scans**: Perform regular vulnerability scans on your infrastructure.
- **Deploy Behind a Reverse Proxy**: Use a reverse proxy like Nginx or Apache with security features enabled.

## Token Security

### JWT Token Configuration

- **Short-lived Tokens**: Configure your SSO server to issue short-lived tokens (15-60 minutes).
- **Use Strong Signing Algorithms**: Ensure tokens use RS256 or ES256 algorithms, not HS256.
- **Validate All Claims**: Verify expiration, issuer, audience, and other claims:
  ```python
  OUA_VERIFY_TOKEN_EXPIRATION = True
  OUA_VERIFY_TOKEN_ISSUER = True
  OUA_ALLOWED_TOKEN_ISSUERS = ['https://sso.company.com']
  ```
- **Limited Token Scope**: Minimize the permissions and data included in tokens.

### Token Blacklisting

- **Implement Token Revocation**: Use the blacklisting feature for sessions that end or are compromised:

  ```python
  from oua_auth import OUAJWTAuthentication

  def logout_view(request):
      if hasattr(request, 'oua_token'):
          OUAJWTAuthentication.revoke_token(
              token=request.oua_token,
              blacklisted_by=request.user.email,
              reason="User logout"
          )
  ```

- **Clean Expired Tokens**: Run a regular task to clean expired blacklisted tokens:

  ```python
  # In management command or celery task
  from oua_auth.models import BlacklistedToken

  count = BlacklistedToken.clean_expired_tokens()
  logger.info(f"Removed {count} expired tokens from blacklist")
  ```

- **Distributed Blacklist**: For multi-server deployments, ensure your database is properly replicated for blacklist consistency.

### CSRF Protection

Even with JWT authentication, CSRF protection is important for browser-based usage:

- **Keep Django's CSRF Middleware**: Don't remove the CSRF middleware.
- **Use CSRF Protection in Forms**: Always use Django's CSRF protection in forms.
- **SameSite Cookies**: Configure cookies with SameSite=Lax or Strict:
  ```python
  SESSION_COOKIE_SAMESITE = 'Lax'
  CSRF_COOKIE_SAMESITE = 'Lax'
  ```

## Access Control

### Principle of Least Privilege

- **Restrict Admin Access**: Limit admin access to only trusted domains and users:
  ```python
  OUA_TRUSTED_ADMIN_DOMAINS = ['admin.company.com']
  OUA_TRUSTED_ADMIN_EMAILS = ['admin@company.com']
  ```
- **Domain Restrictions**: Implement domain restrictions for your user base:
  ```python
  OUA_ALLOWED_DOMAINS = ['company.com', 'trusted-partner.org']
  ```
- **Path Exclusions**: Carefully review which paths are excluded from authentication:
  ```python
  OUA_EXCLUDE_PATHS = [
      '/public/',
      '/api/health/',
      '/static/',
  ]
  ```

### Rate Limiting and Brute Force Protection

- **Implement Rate Limiting**: Configure rate limiting to prevent brute force attacks:
  ```python
  OUA_MAX_AUTH_FAILURES = 5
  OUA_AUTH_FAILURE_WINDOW = 300
  ```
- **Account Locking**: Enable automatic account locking after suspicious activities:
  ```python
  OUA_MAX_SUSPICIOUS_ACTIVITIES = 3
  OUA_SUSPICIOUS_ACTIVITY_WINDOW = 86400  # 24 hours
  OUA_ACCOUNT_LOCK_DURATION = 3600  # 1 hour
  ```
- **Redis Cache**: Use Redis for rate limiting in production environments:
  ```python
  CACHES = {
      'default': {
          'BACKEND': 'django.core.cache.backends.redis.RedisCache',
          'LOCATION': 'redis://redis:6379/1',
      }
  }
  ```

## Headers and Content Security

### Security Headers

Enable all security headers provided by the middleware:

```python
MIDDLEWARE = [
    # ... other middleware ...
    'oua_auth.SecurityHeadersMiddleware',
]
```

Customize the headers for your application:

```python
# Content Security Policy - tighten for your specific needs
OUA_CONTENT_SECURITY_POLICY = "default-src 'self'; script-src 'self'; connect-src 'self'; img-src 'self'; style-src 'self';"

# X-Frame-Options - prevent clickjacking
OUA_FRAME_OPTIONS = "DENY"  # or SAMEORIGIN if frames are needed

# Permissions Policy - limit browser features
OUA_PERMISSIONS_POLICY = "camera=(), microphone=(), geolocation=(), payment=()"
```

### CORS Configuration

If your API serves multiple origins, configure CORS carefully:

```python
INSTALLED_APPS = [
    # ... other apps ...
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    # ... other middleware ...
]

# Specify exactly which origins are allowed
CORS_ALLOWED_ORIGINS = [
    "https://example.com",
    "https://sub.example.com",
]

# Or allow specific patterns
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://\w+\.example\.com$",
]

# Disable credentials for public endpoints
CORS_ALLOW_CREDENTIALS = False
```

## User Security

### Password Management

While OUA Auth uses token-based authentication, password security is still relevant for the SSO server:

- **Enforce Strong Passwords**: Configure your SSO server to require strong passwords.
- **Password Rotation**: Implement periodic password rotation policies.
- **MFA**: Enable Multi-Factor Authentication on your SSO server.

### User Data Protection

- **Minimal User Data**: Store only essential user information in your application.
- **Encrypt Sensitive Data**: Encrypt sensitive user data at rest.
- **Data Retention Policy**: Implement a policy to remove inactive users and their data.

## Monitoring and Incident Response

### Logging

- **Enable Comprehensive Logging**: Configure detailed logging for security events:
  ```python
  LOGGING = {
      # ... other config ...
      'loggers': {
          'oua_auth': {
              'handlers': ['console', 'file'],
              'level': 'INFO',
              'propagate': False,
          },
      },
  }
  ```
- **Centralized Logging**: Send logs to a centralized logging system (ELK, Graylog, etc.).
- **Log Rotation**: Ensure logs are rotated and don't fill up disk space.
- **Redact Sensitive Data**: Enable redaction of sensitive data in logs:
  ```python
  OUA_REDACT_SENSITIVE_DATA = True
  ```

### Monitoring

- **Monitor Authentication Failures**: Set up alerts for unusual authentication failure patterns.
- **Track Suspicious Activities**: Regularly review the `SuspiciousActivity` model entries.
- **Performance Monitoring**: Set up monitoring for performance issues that could indicate DoS attacks.
- **Health Checks**: Implement and monitor health check endpoints that don't expose sensitive information.

### Incident Response

- **Develop an Incident Response Plan**: Have a plan ready for security incidents.
- **Emergency Token Revocation**: Be prepared to revoke all tokens in case of a security breach:

  ```python
  from oua_auth.models import BlacklistedToken
  from django.utils import timezone

  # Emergency revocation of all tokens
  def emergency_revoke_all_tokens():
      # Set a far-future expiration date
      future_date = timezone.now() + timezone.timedelta(days=365)

      # Create a wildcard token pattern or iterate through active users
      # and blacklist tokens for each - implementation depends on your token structure
      BlacklistedToken.add_token_to_blacklist(
          token="ALL_TOKENS",
          expires_at=future_date,
          blacklisted_by="security-team",
          reason="Security incident"
      )
  ```

- **User Notification System**: Have a system to notify users of security incidents.

## Regular Security Maintenance

### Updates and Patching

- **Keep Dependencies Updated**: Regularly update Django and other dependencies:
  ```bash
  pip install --upgrade oua-auth
  pip install --upgrade django
  ```
- **Subscribe to Security Announcements**: Follow the Django security mailing list and other relevant channels.
- **Dependency Scanning**: Use tools like `safety` or Gitlab Dependabot to scan for vulnerable dependencies.

### Security Testing

- **Penetration Testing**: Conduct regular penetration testing of your authentication system.
- **OWASP Top 10 Review**: Regularly review your system against the OWASP Top 10 vulnerabilities.
- **Token Security Testing**: Test token validation, expiration handling, and blacklisting.
- **Authentication Bypass Testing**: Try to bypass authentication using various techniques.

### Code Reviews

- **Security-Focused Code Reviews**: Perform security-focused code reviews for authentication-related code.
- **Static Analysis**: Use static analysis tools to identify security issues.
- **External Audits**: Consider periodic external security audits.

## Recommended Security Tools

- **Security Headers Check**: Use [SecurityHeaders.com](https://securityheaders.com/) to verify your security headers.
- **SSL/TLS Testing**: Use [SSL Labs](https://www.ssllabs.com/ssltest/) to verify your SSL/TLS configuration.
- **OWASP ZAP**: Use [OWASP ZAP](https://www.zaproxy.org/) for automated security testing.
- **JWT Debugging**: Use [JWT.io](https://jwt.io/) for inspecting and debugging JWT tokens (only in development).

## Authentication System Hardening Checklist

Use this checklist to ensure your OUA Authentication deployment is properly hardened:

- [ ] HTTPS is enforced for all connections
- [ ] HSTS is enabled with appropriate settings
- [ ] All security headers are enabled and properly configured
- [ ] JWT tokens use strong signing algorithms
- [ ] Token blacklisting is implemented
- [ ] Rate limiting is configured
- [ ] Automatic account locking is enabled
- [ ] Suspicious activity tracking is enabled
- [ ] Admin access is restricted to trusted domains and emails
- [ ] Domain restrictions are implemented if needed
- [ ] Logging is properly configured with sensitive data redaction
- [ ] Regular token cleanup is scheduled
- [ ] CSRF protection is enabled
- [ ] Dependency updates are routinely applied
- [ ] Security testing is performed regularly
- [ ] Incident response plan is in place
- [ ] Security headers are verified with external tools
- [ ] SSL/TLS configuration is tested with SSL Labs
