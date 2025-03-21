"""
HESTIA Logger - Console Handler.

Defines a structured console handler that outputs logs to the terminal
with proper formatting, including optional colored logs for better visibility.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import logging
import colorlog  # Provides colored console output

__all__ = ["console_handler"]

# Create console handler with a colorized formatter
console_handler = logging.StreamHandler()
console_formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    },
)
console_handler.setFormatter(console_formatter)
console_handler.setLevel(logging.DEBUG)

# Ensure this handler is only imported in `custom_logger.py` and not redefined elsewhere
