"""
HESTIA Logger - Logging Middleware.

Provides middleware functions for logging request and response details
in web applications using FastAPI, Flask, and other frameworks.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import logging
import os
from ..handlers.console_handler import console_handler  # Use global console handler
from ..core.custom_logger import JSONFormatter  # Use JSON formatter

__all__ = ["LoggingMiddleware"]


class LoggingMiddleware:
    """
    Middleware that logs incoming requests and outgoing responses.
    """

    def __init__(self, logger_name="hestia_middleware"):
        """
        Initializes the middleware with a logger instance.
        """
        self.logger = logging.getLogger(logger_name)

        # Load log level from environment variable
        LOG_LEVELS = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        LOG_LEVEL_STR = os.getenv("MIDDLEWARE_LOG_LEVEL", "INFO").upper()
        LOG_LEVEL = LOG_LEVELS.get(LOG_LEVEL_STR, logging.INFO)
        self.logger.setLevel(LOG_LEVEL)

        # Use global console handler
        self.logger.addHandler(console_handler)

        # Use JSON formatting for structured logging
        json_formatter = JSONFormatter()
        file_handler = logging.FileHandler("logs/middleware.log")
        file_handler.setFormatter(json_formatter)
        self.logger.addHandler(file_handler)

        # Prevent log duplication
        self.logger.propagate = False

    def log_request(self, request):
        """
        Logs details of an incoming HTTP request.
        """
        log_entry = {
            "event": "incoming_request",
            "method": request.method,
            "url": str(request.url),
        }
        self.logger.info(log_entry)

    def log_response(self, response):
        """
        Logs details of an outgoing HTTP response.
        """
        log_entry = {
            "event": "outgoing_response",
            "status_code": response.status_code,
        }
        self.logger.info(log_entry)
