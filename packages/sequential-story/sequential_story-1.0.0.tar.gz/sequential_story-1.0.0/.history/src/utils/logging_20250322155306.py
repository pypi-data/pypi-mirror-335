"""Logging module for the Sequential Tools MCP Server.

This module provides a flexible and configurable logging setup for the application.
"""

import logging
import sys

# Create a global instance of the settings
log_settings = LogSettings()

# Module logger
logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """Set up logging configuration."""
    # Create log directory if it doesn't exist

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_settings.LOG_LEVEL)

    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(log_settings.LOG_FORMAT)

    # Add console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Log configuration source
    logger.info("Logging initialized at level: %s", log_settings.LOG_LEVEL)


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module.

    Args:
        name: The name of the module.

    Returns:
        A logger instance.

    """
    return logging.getLogger(name)
