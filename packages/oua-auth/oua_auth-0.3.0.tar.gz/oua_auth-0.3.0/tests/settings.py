"""Django test settings for oua_auth tests."""

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "test-secret-key"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "oua_auth.apps.OUAAppConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Required for URL resolution in tests
ROOT_URLCONF = "tests.urls"

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# OUA SSO settings
OUA_SSO_URL = "https://test-sso.example.com"
OUA_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnzyis1ZjfNB0bBgKFMSv
vkTtwlvBsaJq7S5wA+kzeVOVpVWwkWdVha4s38XM/pa/yr47av7+z3VTmvDRyAHc
aT92whREFpLv9cj5lTeJSibyr/Mrm/YtjCZVWgaOYIhwrXwKLqPr/11inWsAkfIy
tvHWTxZYEcXLgAXFuUuaS3uF9gEiNQwzGTU1v0FqkqTBr4B8nW3HCN47XUu0t8Y0
e+lf4s4OxQawWD79J9/5d3Ry0vbV3Am1FtGJiJvOwRsIfVChDpYStTcHTCMqtvWb
V6L11BWkpzGXSW4Hv43qa+GSYOD2QU68Mb59oSk2OB+BtOLpJofmbGEGgvmwyCI9
MwIDAQAB
-----END PUBLIC KEY-----"""
OUA_CLIENT_ID = "test-client-id"
OUA_TOKEN_SIGNING_KEY = "test-signing-key"
OUA_TOKEN_LEEWAY = 60  # 60 seconds leeway for clock skew handling
OUA_TRUSTED_DOMAINS = ["example.com", "trusted.example.com"]
OUA_TRUSTED_EMAILS = ["specific@email.com"]
OUA_TRUSTED_ADMIN_DOMAINS = ["trusted.example.com"]
OUA_TRUSTED_ADMIN_EMAILS = ["admin@example.com", "superuser@trusted.example.com"]
OUA_TOKEN_AUDIENCE = "test-client-id"
OUA_VERIFY_TIMEOUT = 5
OUA_VALIDATE_AUDIENCE = True
OUA_VALIDATE_EMAIL = True
OUA_ENFORCE_HTTPS = True
OUA_VERIFY_USER_PRIVILEGES = True
OUA_TOKEN_REVOCATION_CHECK = False
OUA_RATE_LIMIT = {
    "ENABLED": True,
    "RATE": "10/m",
    "PATHS": ["/api/"],
}

# Django REST Framework settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "oua_auth.authentication.OUAJWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
}
