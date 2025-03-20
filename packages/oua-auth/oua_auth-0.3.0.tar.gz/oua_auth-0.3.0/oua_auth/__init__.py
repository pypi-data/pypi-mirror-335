"""
Organization Unified Access (OUA) - Django Authentication.

This package provides authentication integration with OUA SSO server for Django projects.
"""

__version__ = "0.3.0"

# Import and initialize logging first to ensure it's ready early
try:
    from .logging_init import initialize_logging

    initialize_logging()
except (ImportError, ModuleNotFoundError):
    import logging

    logging.basicConfig(level=logging.INFO)
    logging.warning("OUA Auth logging initialization failed, using basic configuration")


# Define a lazy loading mechanism for imports
class LazyLoader:
    """Lazily load modules only when accessed."""

    def __init__(self, import_path):
        self.import_path = import_path
        self._module = None

    def __getattr__(self, name):
        if self._module is None:
            import importlib

            self._module = importlib.import_module(self.import_path)
        return getattr(self._module, name)


# Define all modules with a clean API through proxy objects
authentication = LazyLoader(".authentication")
middleware = LazyLoader(".middleware")
backend = LazyLoader(".backend")
security_middleware = LazyLoader(".security_middleware")
logging_utils = LazyLoader(".logging_utils")
models = LazyLoader(".models")

# Define __all__ to expose the intended public API
__all__ = [
    "__version__",
    "authentication",
    "middleware",
    "backend",
    "security_middleware",
    "logging_utils",
    "models",
]

# Note: Token blacklist initialization should be moved to the app's ready() method
# rather than initialized here during module import
