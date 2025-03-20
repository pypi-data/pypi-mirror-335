"""Security middleware for OUA SSO authentication.

This middleware adds important security headers to HTTP responses to protect
against common web vulnerabilities such as XSS, Clickjacking, and CSRF.
"""

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware that adds security-related headers to the response.

    This middleware adds headers that help protect against:
    - Cross-Site Scripting (XSS)
    - Clickjacking
    - MIME-type confusion attacks
    - SSL/TLS downgrade
    - Information leakage
    """

    def __init__(self, get_response=None):
        super().__init__(get_response)

    def _get_setting(self, name, default=None):
        """Get a setting from Django settings with a default value."""
        return getattr(settings, name, default)

    def process_response(self, request, response):
        """Add security headers to the response."""
        # Load settings (with secure defaults)
        content_security_policy = self._get_setting(
            "OUA_CONTENT_SECURITY_POLICY",
            "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'",
        )
        hsts_seconds = self._get_setting("OUA_HSTS_SECONDS", 31536000)  # 1 year
        hsts_include_subdomains = self._get_setting("OUA_HSTS_INCLUDE_SUBDOMAINS", True)
        hsts_preload = self._get_setting("OUA_HSTS_PRELOAD", False)
        frame_options = self._get_setting("OUA_FRAME_OPTIONS", "SAMEORIGIN")
        xss_protection = self._get_setting("OUA_XSS_PROTECTION", "1; mode=block")
        content_type_options = self._get_setting("OUA_CONTENT_TYPE_OPTIONS", "nosniff")
        referrer_policy = self._get_setting(
            "OUA_REFERRER_POLICY", "strict-origin-when-cross-origin"
        )
        permissions_policy = self._get_setting(
            "OUA_PERMISSIONS_POLICY",
            "geolocation=(), microphone=(), camera=(), payment=()",
        )

        # Define which paths to exclude from adding security headers
        exclude_paths = self._get_setting("OUA_SECURITY_HEADERS_EXCLUDE_PATHS", [])

        # Conditionally enable HSTS based on settings
        enable_hsts = self._get_setting("OUA_ENABLE_HSTS", False)

        # Skip excluded paths
        path = request.path
        if any(path.startswith(excluded_path) for excluded_path in exclude_paths):
            return response

        # Set Content Security Policy
        if content_security_policy:
            response["Content-Security-Policy"] = content_security_policy

        # Set HTTP Strict Transport Security (HSTS) only if enabled
        # This should only be enabled if the site is served over HTTPS
        if enable_hsts:
            hsts_header = f"max-age={hsts_seconds}"
            if hsts_include_subdomains:
                hsts_header += "; includeSubDomains"
            if hsts_preload:
                hsts_header += "; preload"
            response["Strict-Transport-Security"] = hsts_header

        # Set X-Frame-Options to protect against clickjacking
        if frame_options:
            response["X-Frame-Options"] = frame_options

        # Set X-XSS-Protection to enable the browser's XSS filter
        if xss_protection:
            response["X-XSS-Protection"] = xss_protection

        # Set X-Content-Type-Options to prevent MIME type sniffing
        if content_type_options:
            response["X-Content-Type-Options"] = content_type_options

        # Set Referrer-Policy to control information in the referer header
        if referrer_policy:
            response["Referrer-Policy"] = referrer_policy

        # Set Permissions-Policy (formerly Feature-Policy) to control browser features
        if permissions_policy:
            response["Permissions-Policy"] = permissions_policy

        return response
