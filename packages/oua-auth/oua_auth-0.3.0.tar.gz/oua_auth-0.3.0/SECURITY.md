# Security Features - OrganizationUnifiedAccess (OUA) Auth

This document provides an overview of security features and best practices implemented in the OrganizationUnifiedAccess (OUA) Authentication package.

## Core Security Features

### JWT Token Validation

- **RSA256 Signature Verification**: Validates token signatures using RSA256 cryptography.
- **Expiration Checking**: Verifies that tokens are not expired.
- **Audience Validation**: Ensures tokens are intended for the correct recipient.
- **Issuer Validation**: Confirms tokens are issued by a trusted authority.

### Input Sanitization

- **HTML Sanitization**: Uses `bleach` to strip dangerous HTML tags and attributes.
- **Length Limitations**: Restricts input length to prevent DoS attacks.
- **Email Validation**: Ensures email addresses follow proper format.
- **XSS Protection**: Removes potentially dangerous characters and scripts.

### Token Blacklisting

- **Immediate Revocation**: Allows instant invalidation of compromised tokens.
- **Distributed Storage**: Works across multiple servers/instances.
- **Automatic Cleanup**: Expired blacklisted tokens are automatically removed.

### Rate Limiting

- **Cache-Based Tracking**: Uses Django's cache framework for distributed rate limiting.
- **IP-Based Limiting**: Prevents brute force attacks from specific sources.
- **User-Based Limiting**: Limits authentication attempts per user.
- **Configurable Thresholds**: Customize limits based on your security requirements.

## Enhanced User Validation

### Domain Restrictions

- **Allowlisting**: Limit access to users from specific trusted domains:
  ```python
  OUA_ALLOWED_DOMAINS = ['company.com', 'trusted-partner.org']
  ```
- **Blocklisting**: Prevent access from specific domains:
  ```python
  OUA_RESTRICTED_DOMAINS = ['competitor.com', 'known-threat.org']
  ```
- **Admin Restrictions**: Additional domain restrictions for admin users:
  ```python
  OUA_TRUSTED_ADMIN_DOMAINS = ['admin.company.com']
  ```

### Required Token Attributes

- Ensure tokens contain all required fields for your application:
  ```python
  OUA_REQUIRED_TOKEN_ATTRIBUTES = ['email', 'name', 'sub', 'groups']
  ```
- Missing required attributes will trigger authentication failure.
- Prevents incomplete or malformed tokens from being accepted.

### Suspicious Activity Detection

The package tracks several types of suspicious activities:

- **Token Reuse**: Attempts to use a token that's been used before.
- **Invalid Origin**: Requests from unexpected IP addresses or locations.
- **Multiple Failed Attempts**: Repeated authentication failures.
- **Unusual Access Patterns**: Access at unusual times or from unusual locations.

Configure suspicious activity detection:

```python
OUA_SUSPICIOUS_ACTIVITY_TYPES = [
    'token_reuse',
    'invalid_origin',
    'unusual_location',
    'multiple_failed_attempts'
]
```

### Automatic Account Locking

The system can automatically lock accounts after detecting suspicious activity:

```python
# Number of suspicious activities before locking
OUA_MAX_SUSPICIOUS_ACTIVITIES = 3

# Time window for counting suspicious activities (24 hours)
OUA_SUSPICIOUS_ACTIVITY_WINDOW = 86400

# How long accounts remain locked (24 hours)
OUA_ACCOUNT_LOCK_DURATION = 86400
```

Locked accounts can be manually unlocked by administrators through the Django admin interface.

## Security Headers

The package includes a middleware component that sets various security-related HTTP headers:

```python
MIDDLEWARE = [
    # ... other middleware ...
    'oua_auth.SecurityHeadersMiddleware',
]
```

Headers implemented:

- **Strict-Transport-Security (HSTS)**: Enforces HTTPS connections.
- **Content-Security-Policy (CSP)**: Prevents XSS and data injection attacks.
- **X-Content-Type-Options**: Prevents MIME type sniffing.
- **X-Frame-Options**: Protects against clickjacking.
- **Referrer-Policy**: Controls information in the Referer header.
- **Permissions-Policy**: Limits which browser features can be used.
- **X-XSS-Protection**: Additional XSS protection for older browsers.

## Structured Logging

The package includes a structured logging system that:

- **Redacts Sensitive Data**: Automatically redacts tokens, passwords, and other sensitive information.
- **Standardizes Format**: Uses a consistent JSON format for logs.
- **Includes Context**: Adds request/user context to all log entries.
- **Provides Audit Trail**: Records authentication events for security auditing.

## Best Practices

### Configuration Recommendations

1. **Use HTTPS**: Always deploy with HTTPS in production.
2. **Set Strong Rate Limits**: Adjust rate limits based on your application's expected traffic.
3. **Enable Account Locking**: Use automatic account locking for sensitive applications.
4. **Configure Required Attributes**: Specify all token attributes your application requires.
5. **Implement Domain Restrictions**: Use domain allowlists for sensitive applications.
6. **Set Security Headers**: Enable all security headers in production.

### Monitoring and Auditing

1. **Review Suspicious Activities**: Regularly check the `SuspiciousActivity` model in the admin interface.
2. **Monitor Authentication Logs**: Watch for patterns of failed authentication.
3. **Audit Admin Access**: Review which users have accessed admin functionality.
4. **Check Blacklisted Tokens**: Investigate why tokens were blacklisted.

## Reporting Security Issues

If you discover a security vulnerability in this package, please report it by sending an email to alexmungai964@gmail.com. Please do not report security vulnerabilities through public Gitlab issues.

Your report should include:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested mitigations (if you have them)

We will acknowledge receipt of your report within 24 hours and send you regular updates about our progress.
