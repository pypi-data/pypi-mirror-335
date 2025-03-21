"""
HESTIA Logger - Middlewares Module.

Provides middleware for request logging in web frameworks.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

# Expose middleware module
from .middleware import LoggingMiddleware


# Define public API for `middlewares`
__all__ = ["LoggingMiddleware"]
