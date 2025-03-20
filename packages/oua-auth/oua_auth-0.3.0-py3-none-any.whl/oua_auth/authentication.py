from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta, UTC
import bleach
import hashlib
import re
import uuid

# Switch to our enhanced logging
from .logging_utils import setup_logging

# Set up module logger with context
logger = setup_logging(__name__)

# Import our model if available, otherwise use in-memory tracking as fallback
try:
    from oua_auth.models import BlacklistedToken, SuspiciousActivity

    BLACKLIST_DB_AVAILABLE = True
    SUSPICIOUS_ACTIVITY_DB_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    # If the model isn't available (Django not fully loaded), use in-memory
    logger.warning("BlacklistedToken model not available, using in-memory blacklist")
    BLACKLIST_DB_AVAILABLE = False
    SUSPICIOUS_ACTIVITY_DB_AVAILABLE = False


class OUAJWTAuthentication(BaseAuthentication):
    """
    Django Rest Framework authentication class for Organization Unified Access (OUA).
    Validates JWT tokens and creates/updates users based on token claims.
    """

    # Class-level storage for instances (used for in-memory blacklist access)
    _instances = []

    def __init__(self):
        # Get optional settings with defaults
        self.token_signing_key = getattr(
            settings, "OUA_TOKEN_SIGNING_KEY", settings.SECRET_KEY
        )

        # Admin privilege controls
        self.trusted_admin_domains = getattr(settings, "OUA_TRUSTED_ADMIN_DOMAINS", [])
        self.trusted_admin_emails = getattr(settings, "OUA_TRUSTED_ADMIN_EMAILS", [])

        # Token lifetime
        self.internal_token_lifetime = getattr(
            settings, "OUA_INTERNAL_TOKEN_LIFETIME", 3600
        )  # 1 hour

        # Rate limiting configuration
        self.max_failures = getattr(settings, "OUA_MAX_AUTH_FAILURES", 5)
        self.failure_window = getattr(
            settings, "OUA_AUTH_FAILURE_WINDOW", 300
        )  # 5 minutes

        # Cache configuration
        self.cache_timeout = getattr(
            settings, "OUA_RATELIMIT_CACHE_TIMEOUT", self.failure_window
        )
        self.cache_prefix = getattr(
            settings, "OUA_RATELIMIT_CACHE_PREFIX", "oua_auth_failure"
        )

        # Token blacklist configuration - only for in-memory fallback
        self._token_blacklist = set()

        # New validation options
        # Domain restrictions for all users
        self.allowed_domains = getattr(settings, "OUA_ALLOWED_DOMAINS", [])
        self.restricted_domains = getattr(settings, "OUA_RESTRICTED_DOMAINS", [])

        # Required token attributes
        self.required_token_attributes = getattr(
            settings, "OUA_REQUIRED_TOKEN_ATTRIBUTES", []
        )

        # Account locking configuration
        self.max_suspicious_activities = getattr(
            settings, "OUA_MAX_SUSPICIOUS_ACTIVITIES", 3
        )
        self.suspicious_activity_window = getattr(
            settings, "OUA_SUSPICIOUS_ACTIVITY_WINDOW", 86400
        )  # 24 hours
        self.account_lock_duration = getattr(
            settings, "OUA_ACCOUNT_LOCK_DURATION", 86400
        )  # 24 hours

        # Suspicious activities that trigger account locking
        self.suspicious_activity_types = getattr(
            settings,
            "OUA_SUSPICIOUS_ACTIVITY_TYPES",
            [
                "token_reuse",
                "invalid_origin",
                "unusual_location",
                "multiple_failed_attempts",
            ],
        )

        # Register this instance if using in-memory blacklist
        if not BLACKLIST_DB_AVAILABLE:
            if not hasattr(OUAJWTAuthentication, "_instances"):
                OUAJWTAuthentication._instances = []
            OUAJWTAuthentication._instances.append(self)

        # Create instance-specific logger with context
        self.log = logger.with_context(
            component="authentication",
            subsystem="jwt_auth",
            instance_id=str(id(self))[-8:],
        )

        self.log.debug(
            "Initialized OUAJWTAuthentication",
            extra={
                "max_failures": self.max_failures,
                "failure_window": self.failure_window,
                "trusted_domains_count": len(self.trusted_admin_domains),
                "trusted_emails_count": len(self.trusted_admin_emails),
                "allowed_domains_count": len(self.allowed_domains),
                "restricted_domains_count": len(self.restricted_domains),
                "required_attributes_count": len(self.required_token_attributes),
            },
        )

    def authenticate(self, request):
        # Get token from Authorization header
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]

        # Create request-specific logger with client context
        client_ip = self._get_client_ip(request)
        req_log = self.log.with_context(
            request_id=getattr(request, "id", str(uuid.uuid4())),
            ip_address=client_ip,
            user_agent=request.META.get("HTTP_USER_AGENT", "Unknown"),
        )

        # Check for rate limiting
        if self._is_rate_limited(request):
            req_log.warning(
                "Authentication rate limited", extra={"ip_address": client_ip}
            )
            raise AuthenticationFailed(
                "Too many failed attempts. Please try again later."
            )

        # Check if token is blacklisted
        if self._is_token_blacklisted(token):
            req_log.warning("Attempt to use blacklisted token")
            raise AuthenticationFailed("Token has been revoked")

        try:
            # Get token leeway setting for clock skew handling
            token_leeway = getattr(settings, "OUA_TOKEN_LEEWAY", 0)

            # Verify and decode the JWT token with explicit options
            payload = jwt.decode(
                token,
                settings.OUA_PUBLIC_KEY,
                algorithms=["RS256"],
                audience=settings.OUA_CLIENT_ID,
                options={
                    "verify_exp": True,
                    "verify_aud": True,
                    "verify_signature": True,
                    "verify_iat": True,  # Verify issued at time if present
                    "verify_nbf": True,  # Verify not before time if present
                    "require_exp": True,  # Require expiration time
                    "leeway": token_leeway,  # Add leeway for clock skew between servers
                },
            )

            # Log clock skew handling if leeway is enabled
            if token_leeway > 0:
                req_log.debug(
                    "Using token leeway for clock skew handling",
                    extra={"leeway_seconds": token_leeway},
                )

            # Additional token validation
            if "iat" in payload:
                # Reject tokens issued too far in the past (e.g., 24 hours)
                iat_timestamp = payload["iat"]
                token_age = datetime.now(UTC) - datetime.fromtimestamp(
                    iat_timestamp, UTC
                )
                max_token_age = timedelta(hours=24)
                if token_age > max_token_age:
                    req_log.warning(
                        "Token too old",
                        extra={
                            "token_age_seconds": token_age.total_seconds(),
                            "max_age_seconds": max_token_age.total_seconds(),
                        },
                    )
                    raise AuthenticationFailed("Token is too old")

            # Check for required token attributes
            if self.required_token_attributes:
                missing_attributes = [
                    attr
                    for attr in self.required_token_attributes
                    if attr not in payload
                ]
                if missing_attributes:
                    req_log.warning(
                        "Missing required token attributes",
                        extra={"missing_attributes": missing_attributes},
                    )
                    self._record_auth_failure(client_ip)
                    self._record_suspicious_activity(
                        None,
                        client_ip,
                        "missing_required_attributes",
                        details=f"Missing attributes: {', '.join(missing_attributes)}",
                    )
                    raise AuthenticationFailed(
                        f"Missing required token attributes: {', '.join(missing_attributes)}"
                    )

            # Get or create user based on email
            User = get_user_model()
            email = payload.get("email")
            if not email:
                self._record_auth_failure(client_ip)
                raise AuthenticationFailed("Invalid token: no email claim")

            # Basic email format validation
            if not self._validate_email_format(email):
                req_log.error("Invalid email format in token", extra={"email": email})
                self._record_auth_failure(client_ip)
                raise AuthenticationFailed("Invalid email format in token")

            # Check domain restrictions for all users
            if self.allowed_domains or self.restricted_domains:
                domain = email.split("@")[-1].lower()

                # If allowed domains are specified, only these domains are permitted
                if self.allowed_domains and domain not in self.allowed_domains:
                    req_log.warning(
                        "User domain not in allowed domains list",
                        extra={"email": email, "domain": domain},
                    )
                    self._record_auth_failure(client_ip)
                    self._record_suspicious_activity(
                        email,
                        client_ip,
                        "domain_not_allowed",
                        details=f"Domain {domain} not in allowed list",
                    )
                    raise AuthenticationFailed(
                        "Your email domain is not authorized to access this system"
                    )

                # If restricted domains are specified, these domains are not permitted
                if self.restricted_domains and domain in self.restricted_domains:
                    req_log.warning(
                        "User domain in restricted domains list",
                        extra={"email": email, "domain": domain},
                    )
                    self._record_auth_failure(client_ip)
                    self._record_suspicious_activity(
                        email,
                        client_ip,
                        "domain_restricted",
                        details=f"Domain {domain} in restricted list",
                    )
                    raise AuthenticationFailed(
                        "Your email domain is restricted from accessing this system"
                    )

            # Sanitize user input from token
            sanitized_first_name = self._sanitize_input(payload.get("given_name", ""))
            sanitized_last_name = self._sanitize_input(payload.get("family_name", ""))

            # Check if the account is locked
            if self._is_account_locked(email):
                req_log.warning(
                    "Account locked due to suspicious activity",
                    extra={"email": email},
                )
                raise AuthenticationFailed(
                    "Your account is temporarily locked due to suspicious activity. Please contact support."
                )

            # Get or create the user
            try:
                user = User.objects.get(email=email)
                # Check if user-level lock is set
                if getattr(user, "is_locked", False):
                    lock_reason = getattr(user, "lock_reason", "Unknown reason")
                    lock_until = getattr(user, "locked_until", None)
                    req_log.warning(
                        "User account locked",
                        extra={
                            "email": email,
                            "reason": lock_reason,
                            "locked_until": (
                                str(lock_until) if lock_until else "indefinite"
                            ),
                        },
                    )
                    raise AuthenticationFailed(f"Your account is locked: {lock_reason}")

                # User exists, update fields if necessary
                update_fields = []
                if user.first_name != sanitized_first_name:
                    user.first_name = sanitized_first_name
                    update_fields.append("first_name")
                if user.last_name != sanitized_last_name:
                    user.last_name = sanitized_last_name
                    update_fields.append("last_name")
                if update_fields:
                    user.save(update_fields=update_fields)

            except User.DoesNotExist:
                # Create new user
                user = User.objects.create(
                    email=email,
                    username=email,
                    first_name=sanitized_first_name,
                    last_name=sanitized_last_name,
                    is_active=True,
                )

            # Update request-specific logger with user context
            req_log = req_log.with_context(
                user_id=user.id,
                user_email=user.email,
                is_new_user=user is not None,
            )

            # Update user roles based on token claims with security checks
            roles = payload.get("roles", [])
            if "admin" in roles:
                # Only grant admin if email is from trusted domain or in trusted emails list
                is_trusted = self._is_trusted_admin(email)

                if is_trusted and not user.is_staff:
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()
                    req_log.info(
                        "Admin privileges granted to trusted user",
                        extra={
                            "email": email,
                            "roles": roles,
                        },
                    )
                elif not is_trusted and (user.is_staff or user.is_superuser):
                    # Remove admin privileges if the user is not trusted
                    user.is_staff = False
                    user.is_superuser = False
                    user.save()
                    req_log.warning(
                        "Admin privileges revoked from untrusted user",
                        extra={
                            "email": email,
                            "roles": roles,
                        },
                    )

            # Store token data for access in views
            request.oua_token = token
            request.oua_claims = payload

            # Generate and set internal token
            internal_token = self._generate_internal_token(user, payload)
            request.internal_token = internal_token

            # Log successful authentication
            self._log_auth_success(request, user, payload)

            return (user, internal_token)

        except ExpiredSignatureError:
            req_log.warning("Expired JWT token received")
            self._record_auth_failure(client_ip)
            raise AuthenticationFailed("Token expired")
        except JWTError as e:
            # Don't log the actual token
            req_log.error(
                f"JWT validation error: {type(e).__name__}",
                extra={"error_details": str(e).replace(token, "[REDACTED]")},
            )
            self._record_auth_failure(client_ip)
            raise AuthenticationFailed("Invalid token")
        except AuthenticationFailed as e:
            # Re-raise authentication failures with original message
            req_log.error(f"Authentication error: {e}")
            self._record_auth_failure(client_ip)
            raise
        except Exception as e:
            # Add detailed logging with traceback
            req_log.exception(
                f"Authentication error: {type(e).__name__}",
                extra={"error_class": type(e).__name__},
            )
            # Add request identifier to help trace issues
            request_id = getattr(request, "id", str(uuid.uuid4()))
            req_log.error(f"Request ID: {request_id}")
            self._record_auth_failure(client_ip)
            raise AuthenticationFailed(f"Authentication failed (ID: {request_id})")

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response.
        """
        return "Bearer"

    def _get_client_ip(self, request):
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    def _is_rate_limited(self, request):
        """
        Check if client IP is rate limited due to too many failures.

        Uses Django's cache framework for distributed rate limiting.
        """
        client_ip = self._get_client_ip(request)
        # Skip rate limiting check if setting is disabled
        if not getattr(settings, "OUA_RATE_LIMIT", {}).get("ENABLED", False):
            return False

        # Check if the request path should be rate limited
        if hasattr(settings, "OUA_RATE_LIMIT") and "PATHS" in settings.OUA_RATE_LIMIT:
            # Skip rate limiting if the path doesn't match any of the configured paths
            if not any(
                request.path.startswith(path)
                for path in settings.OUA_RATE_LIMIT["PATHS"]
            ):
                return False

        # Create a cache key specific to this IP - sanitize for memcached compatibility
        # Sanitize the prefix first to make sure it's safe for memcached
        safe_prefix = re.sub(r"[^a-zA-Z0-9_]", "_", str(self.cache_prefix))
        # Sanitize the client IP - replace dots and special chars with underscores
        safe_ip = re.sub(r"[^a-zA-Z0-9_]", "_", client_ip)
        cache_key = f"auth_rate_limit:{safe_prefix}:{safe_ip}"

        # Get the current failure count from cache
        failures = cache.get(cache_key, [])

        if not failures:
            return False

        # Clean up old entries
        now = datetime.now(UTC).timestamp()
        current_failures = [ts for ts in failures if (now - ts) < self.failure_window]

        # Update cache with cleaned list if it changed
        if len(current_failures) != len(failures):
            # Only update if there are still failures to track
            if current_failures:
                cache.set(cache_key, current_failures, self.cache_timeout)
            else:
                cache.delete(cache_key)

        # Check if rate limited
        is_limited = len(current_failures) >= self.max_failures

        # Log rate limit status for debugging
        if is_limited:
            self.log.warning(
                f"Rate limit triggered for IP {client_ip}",
                extra={
                    "ip_address": client_ip,
                    "failure_count": len(current_failures),
                    "max_failures": self.max_failures,
                },
            )

        return is_limited

    def _record_auth_failure(self, client_ip):
        """
        Record an authentication failure for rate limiting

        Uses Django's cache framework for distributed tracking.
        """
        # Create a cache key specific to this IP - sanitize for memcached compatibility
        safe_prefix = re.sub(r"[^a-zA-Z0-9_]", "_", str(self.cache_prefix))
        safe_ip = re.sub(r"[^a-zA-Z0-9_]", "_", client_ip)
        cache_key = f"auth_rate_limit:{safe_prefix}:{safe_ip}"

        # Get the current failure list from cache (or empty list if not found)
        failures = cache.get(cache_key, [])

        # Add the current timestamp
        now = datetime.now(UTC).timestamp()
        failures.append(now)

        # Store the updated list back in cache
        cache.set(cache_key, failures, self.cache_timeout)

        # Log the failure
        self.log.info(
            f"Authentication failure recorded for IP {client_ip}",
            extra={
                "ip_address": client_ip,
                "failure_count": len(failures),
                "max_failures": self.max_failures,
            },
        )

    def _is_token_blacklisted(self, token):
        """Check if token is blacklisted"""
        if BLACKLIST_DB_AVAILABLE:
            # Use the database blacklist if available
            try:
                return BlacklistedToken.is_token_blacklisted(token)
            except Exception as e:
                # Log the error and fall back to in-memory blacklist
                self.log.error(
                    f"Error checking token blacklist: {e}",
                    extra={"error_class": type(e).__name__},
                    exc_info=True,
                )
                token_hash = hashlib.sha256(token.encode()).hexdigest()
                return token_hash in self._token_blacklist
        else:
            # Use in-memory blacklist as fallback
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            return token_hash in self._token_blacklist

    @classmethod
    def revoke_token(cls, token, blacklisted_by=None, reason=None):
        """Revoke a token by adding it to the blacklist

        Args:
            token: The JWT token to blacklist
            blacklisted_by: Optional identifier of who blacklisted the token
            reason: Optional reason for blacklisting

        Returns:
            bool: True if token was successfully blacklisted
        """
        # Get a logger for this class method
        log = setup_logging(__name__).with_context(
            component="authentication",
            function="revoke_token",
        )

        if BLACKLIST_DB_AVAILABLE:
            try:
                # Try to decode the token to get its expiration time
                try:
                    payload = jwt.decode(
                        token,
                        settings.OUA_PUBLIC_KEY,
                        algorithms=["RS256"],
                        options={"verify_signature": True},
                    )
                    # Use token expiration from payload if available
                    if "exp" in payload:
                        expires_at = datetime.fromtimestamp(payload["exp"], UTC)
                    else:
                        # Default to 24 hours from now if no expiration in token
                        expires_at = datetime.now(UTC) + timedelta(hours=24)
                except Exception as e:
                    # If token can't be decoded, use default expiration
                    log.warning(
                        "Error decoding token for blacklisting, using default expiration",
                        extra={"error": str(e), "error_class": type(e).__name__},
                    )
                    expires_at = datetime.now(UTC) + timedelta(hours=24)

                # Add to database blacklist
                BlacklistedToken.add_token_to_blacklist(
                    token=token,
                    expires_at=expires_at,
                    blacklisted_by=blacklisted_by,
                    reason=reason,
                )

                log.info(
                    "Token added to blacklist",
                    extra={
                        "blacklisted_by": blacklisted_by,
                        "reason": reason,
                        "expires_at": expires_at.isoformat(),
                    },
                )

                return True
            except Exception as e:
                # Log the error and fall back to in-memory blacklist
                log.error(
                    f"Error adding token to blacklist: {e}",
                    extra={"error_class": type(e).__name__},
                    exc_info=True,
                )
                token_hash = hashlib.sha256(token.encode()).hexdigest()
                # Try to add to all in-memory instances as fallback
                for instance in cls._instances if hasattr(cls, "_instances") else []:
                    instance._token_blacklist.add(token_hash)
                log.info("Token added to in-memory blacklist (fallback)")
                return True
        else:
            # Use in-memory blacklist as fallback
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            # Add to all in-memory instances
            for instance in cls._instances if hasattr(cls, "_instances") else []:
                instance._token_blacklist.add(token_hash)
            log.info(
                "Token added to in-memory blacklist",
                extra={
                    "blacklisted_by": blacklisted_by,
                    "reason": reason,
                },
            )
            return True

    def _log_auth_success(self, request, user, payload):
        """Log detailed authentication information for auditing"""
        client_ip = self._get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "Unknown")

        audit_data = {
            "event": "authentication_success",
            "user_id": user.id,
            "user_email": user.email,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "is_admin": user.is_staff,
            "timestamp": datetime.now(UTC).isoformat(),
            "token_sub": payload.get("sub", "Unknown"),
            "token_exp": payload.get("exp", 0),
        }

        # Log as JSON with all context data
        self.log.info(
            "Authentication successful",
            extra={
                "audit": audit_data,
                "request_id": getattr(request, "id", None),
            },
        )

    def _generate_internal_token(self, user, external_payload):
        """
        Generate an internal token based on the external token payload
        and user information with enhanced security.
        """
        try:
            # Calculate expiration time (default: 1 hour from now)
            exp_time = datetime.now(UTC) + timedelta(
                seconds=self.internal_token_lifetime
            )

            # Create a unique token ID
            token_id = hashlib.sha256(
                f"{user.id}:{datetime.now(UTC).timestamp()}".encode()
            ).hexdigest()

            # Essential claims
            internal_claims = {
                "user_id": user.id,
                "email": user.email,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
                "exp": int(exp_time.timestamp()),
                "iat": int(datetime.now(UTC).timestamp()),
                "jti": token_id,
            }

            # Copy important claims from external payload
            for key in ["roles", "given_name", "family_name", "sub"]:
                if key in external_payload:
                    if key == "roles":
                        internal_claims["external_roles"] = external_payload[key]
                    else:
                        internal_claims[key] = external_payload[key]

            # Sign with dedicated signing key (separate from SECRET_KEY)
            token = jwt.encode(
                internal_claims, self.token_signing_key, algorithm="HS256"
            )

            # Clear sensitive data from memory as soon as possible
            internal_claims.clear()

            # Log token generation without sensitive details
            self.log.debug(
                "Internal token generated",
                extra={
                    "user_id": user.id,
                    "token_id": token_id,
                    "expires_at": exp_time.isoformat(),
                },
            )

            return token

        except Exception as e:
            # Clear sensitive data even on error
            if "internal_claims" in locals():
                internal_claims.clear()
            self.log.error(
                f"Error generating internal token: {type(e).__name__}",
                extra={"error_class": type(e).__name__},
                exc_info=True,
            )
            raise

    def _sanitize_input(self, input_value):
        """
        Enhanced input sanitization to prevent XSS and injection attacks.
        Uses bleach library to clean HTML content by stripping all tags
        and attributes except those explicitly allowed.

        Args:
            input_value: The raw input value to sanitize

        Returns:
            str: The sanitized input value
        """
        if not isinstance(input_value, str):
            # If not a string, just return as is
            return input_value

        # Define allowed tags and attributes (empty lists mean no tags or attributes allowed)
        allowed_tags = []
        allowed_attributes = {}

        # Use bleach to clean the input, stripping all HTML tags
        sanitized = bleach.clean(
            input_value, tags=allowed_tags, attributes=allowed_attributes, strip=True
        )

        # Strip whitespace and normalize spaces
        sanitized = " ".join(sanitized.split())

        # Limit length of input to prevent DoS attacks
        max_length = 100
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]

        return sanitized

    def _validate_email_format(self, email):
        """Validate basic email format"""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    def _is_trusted_admin(self, email):
        """Check if the email is from trusted domain or in trusted emails list"""
        if email in self.trusted_admin_emails:
            return True

        if self.trusted_admin_domains:
            domain = email.split("@")[-1].lower()
            return domain in self.trusted_admin_domains

        # If no restrictions set, default to allowing (backward compatibility)
        return (
            len(self.trusted_admin_domains) == 0 and len(self.trusted_admin_emails) == 0
        )

    def _is_account_locked(self, email):
        """
        Check if an account should be locked due to suspicious activity.

        Uses the database if available, otherwise falls back to cache.
        """
        if not email:
            return False

        # Use database if available
        if SUSPICIOUS_ACTIVITY_DB_AVAILABLE:
            try:
                # Check if there's an explicit lock
                User = get_user_model()
                try:
                    user = User.objects.get(email=email)
                    if hasattr(user, "is_locked") and user.is_locked:
                        locked_until = getattr(user, "locked_until", None)
                        if locked_until and locked_until > datetime.now(UTC):
                            return True
                except User.DoesNotExist:
                    pass

                # Check for suspicious activities threshold
                activity_count = SuspiciousActivity.objects.filter(
                    user_identifier=email,
                    timestamp__gte=datetime.now(UTC)
                    - timedelta(seconds=self.suspicious_activity_window),
                    activity_type__in=self.suspicious_activity_types,
                ).count()

                return activity_count >= self.max_suspicious_activities

            except Exception as e:
                self.log.error(
                    f"Error checking account lock: {e}",
                    extra={"error_class": type(e).__name__, "email": email},
                    exc_info=True,
                )
                # Fall back to cache if database check fails
                pass

        # If database not available, use cache
        # Sanitize email for memcached compatibility
        safe_email = re.sub(r"[^a-zA-Z0-9_]", "_", email)
        cache_key = f"oua_account_lock:{safe_email}"
        lock_info = cache.get(cache_key)

        if not lock_info:
            # Check for suspicious activities count in cache
            # Sanitize the activities key too
            activities_key = f"oua_suspicious_activities:{safe_email}"
            activities = cache.get(activities_key, [])

            # Clean up old activities
            now = datetime.now(UTC).timestamp()
            current_activities = [
                act
                for act in activities
                if (now - act.get("timestamp", 0)) < self.suspicious_activity_window
            ]

            # Only count activities of specified types
            suspicious_count = sum(
                1
                for act in current_activities
                if act.get("type") in self.suspicious_activity_types
            )

            # Update cache if list changed
            if len(current_activities) != len(activities):
                if current_activities:
                    cache.set(
                        activities_key,
                        current_activities,
                        self.suspicious_activity_window,
                    )
                else:
                    cache.delete(activities_key)

            # Check if account should be locked
            is_locked = suspicious_count >= self.max_suspicious_activities

            # If it should be locked, create lock info
            if is_locked:
                lock_info = {
                    "reason": "Too many suspicious activities",
                    "timestamp": now,
                    "expires": now + self.account_lock_duration,
                }
                cache.set(cache_key, lock_info, self.account_lock_duration)

            return is_locked
        else:
            # Check if lock has expired
            if lock_info.get("expires", 0) <= datetime.now(UTC).timestamp():
                cache.delete(cache_key)
                return False
            return True

    def _record_suspicious_activity(
        self, user_identifier, ip_address, activity_type, details=None
    ):
        """
        Record suspicious activity for potential account locking.

        Args:
            user_identifier: Email or other identifier of the user
            ip_address: IP address where the activity originated
            activity_type: Type of suspicious activity
            details: Additional details about the activity
        """
        if not user_identifier and not ip_address:
            return

        now = datetime.now(UTC)
        activity_data = {
            "timestamp": now.timestamp(),
            "ip_address": ip_address,
            "type": activity_type,
            "details": details or "",
        }

        # Use database if available
        if SUSPICIOUS_ACTIVITY_DB_AVAILABLE and user_identifier:
            try:
                SuspiciousActivity.objects.create(
                    user_identifier=user_identifier,
                    ip_address=ip_address,
                    activity_type=activity_type,
                    details=details or "",
                    timestamp=now,
                )

                # Check if we need to lock the account
                if activity_type in self.suspicious_activity_types:
                    activity_count = SuspiciousActivity.objects.filter(
                        user_identifier=user_identifier,
                        timestamp__gte=now
                        - timedelta(seconds=self.suspicious_activity_window),
                        activity_type__in=self.suspicious_activity_types,
                    ).count()

                    if activity_count >= self.max_suspicious_activities:
                        # Try to lock user account if model supports it
                        User = get_user_model()
                        try:
                            user = User.objects.get(email=user_identifier)
                            if hasattr(user, "is_locked"):
                                user.is_locked = True
                                user.lock_reason = (
                                    f"Multiple suspicious activities detected"
                                )
                                if hasattr(user, "locked_until"):
                                    user.locked_until = now + timedelta(
                                        seconds=self.account_lock_duration
                                    )
                                user.save(
                                    update_fields=[
                                        "is_locked",
                                        "lock_reason",
                                        "locked_until",
                                    ]
                                )
                                self.log.warning(
                                    f"Locked account due to suspicious activity",
                                    extra={
                                        "email": user_identifier,
                                        "activity_count": activity_count,
                                        "duration": self.account_lock_duration,
                                    },
                                )
                        except (User.DoesNotExist, AttributeError):
                            pass

                return

            except Exception as e:
                self.log.error(
                    f"Error recording suspicious activity to database: {e}",
                    extra={"error_class": type(e).__name__},
                    exc_info=True,
                )
                # Fall back to cache

        # Use cache for both IP and user-based tracking
        if ip_address:
            # Sanitize IP address for memcached compatibility
            safe_ip = re.sub(r"[^a-zA-Z0-9_]", "_", ip_address)
            ip_key = f"oua_suspicious_activities_ip_{safe_ip}"
            ip_activities = cache.get(ip_key, [])
            ip_activities.append(activity_data)
            cache.set(ip_key, ip_activities, self.suspicious_activity_window)

        if user_identifier:
            # Sanitize user identifier for memcached compatibility
            safe_user = re.sub(r"[^a-zA-Z0-9_]", "_", user_identifier)
            user_key = f"oua_suspicious_activities_{safe_user}"
            user_activities = cache.get(user_key, [])
            user_activities.append(activity_data)
            cache.set(user_key, user_activities, self.suspicious_activity_window)

            # Check if we need to lock the account
            if activity_type in self.suspicious_activity_types:
                recent_activities = [
                    a
                    for a in user_activities
                    if a.get("timestamp", 0)
                    >= now.timestamp() - self.suspicious_activity_window
                    and a.get("type") in self.suspicious_activity_types
                ]

                if len(recent_activities) >= self.max_suspicious_activities:
                    lock_key = f"oua_account_lock_{safe_user}"
                    lock_info = {
                        "timestamp": now.timestamp(),
                        "reason": f"Multiple suspicious activities: {len(recent_activities)}",
                        "expires": now.timestamp() + self.account_lock_duration,
                    }
                    cache.set(lock_key, lock_info, self.account_lock_duration)
                    self.log.warning(
                        f"Locked account due to suspicious activity",
                        extra={
                            "user_identifier": user_identifier,
                            "activity_count": len(recent_activities),
                            "duration": self.account_lock_duration,
                        },
                    )

        self.log.info(
            f"Recorded suspicious activity: {activity_type}",
            extra={
                "user_identifier": user_identifier,
                "ip_address": ip_address,
                "activity_type": activity_type,
                "details": details,
            },
        )
