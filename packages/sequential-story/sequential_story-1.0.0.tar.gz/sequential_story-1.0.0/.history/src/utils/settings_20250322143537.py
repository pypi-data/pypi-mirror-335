"""Logging module for the Sequential Tools MCP Server.

This module provides a flexible and configurable logging setup for the application.
"""

import logging
import sys
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogSettings(BaseSettings):
    """Logging settings.

    Provides a centralized configuration for logging with environment variable support.
    """

    APP_NAME: str = Field(
        default="Sequential Tools MCP Server",
        description="The name of the application.",
    )
    LOG_LEVEL: str = Field(
        default="INFO",
        description="The logging level.",
    )
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="The log message format.",
    )
    LOG_FILE: str = Field(
        default="logs/sequential_tools.log",
        description="Path to the log file.",
    )

    # Paths
    LOG_DIR: Path = Field(
        default_factory=lambda: Path("logs"),
        description="Directory for log files.",
    )

    model_config = SettingsConfigDict(
        env_prefix="SEQUENTIAL_TOOLS_",
        extra="ignore",
    )


# Create a global instance of the settings
log_settings = LogSettings()

# Module logger
logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """Set up logging configuration."""
    # Create log directory if it doesn't exist
    log_file = Path(log_settings.LOG_FILE)
    log_file.parent.mkdir(parents=True, exist_ok=True)

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

    # Add file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Log configuration source
    logger = get_logger(__name__)
    logger.info("Logging initialized at level: %s", log_settings.LOG_LEVEL)


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module.

    Args:
        name: The name of the module.

    Returns:
        A logger instance.

    """
    return logging.getLogger(name)
