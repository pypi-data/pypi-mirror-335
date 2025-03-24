"""Logging module for the Sequential Tools MCP Server.

This module provides a flexible and configurable logging setup for the application.
"""

import logging
import sys

from src.utils.settings import get_settings

settings = get_settings()

# Module logger
logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """Set up logging configuration."""
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)

    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(settings.LOG_FORMAT)

    # Add console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Log configuration source
    logger.info("Logging initialized at level: %s", settings.LOG_LEVEL)


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module.

    Args:
        name: The name of the module.

    Returns:
        A logger instance.

    """
    return logging.getLogger(name)
