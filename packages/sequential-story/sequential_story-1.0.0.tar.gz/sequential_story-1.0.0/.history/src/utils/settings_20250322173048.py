"""Settings module for Sequential Tools MCP Server.

This module provides a flexible and type-safe way to manage application settings
for the Sequential Tools server, using Pydantic for configuration.
"""

from enum import StrEnum

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ToolType(StrEnum):
    """Available tool types for Sequential Tools server."""

    STORY = "story"
    THINKING = "thinking"


class Settings(BaseSettings):
    """Application settings for Sequential Tools MCP Server."""

    model_config = SettingsConfigDict(
        env_prefix="",
        json_encoders={},  # Disable JSON encoding for env vars
        json_schema_extra={"env_json_parser": None},  # Disable JSON parsing for env vars
    )

    # Basic application info
    APP_NAME: str = Field(
        default="Sequential Tools MCP Server",
        description="The name of the application.",
    )
    APP_VERSION: str = Field(
        default="0.1.0",
        description="The version of the application.",
    )

    LOG_LEVEL: str = Field(
        default="INFO",
        description="The logging level.",
    )
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="The log message format.",
    )

    # Tool configuration
    tools: list[ToolType] = Field(
        default=[ToolType.STORY],
        description="List of tools to enable. If None, all tools are enabled.",
    )

    @property
    def enabled_tools(self) -> list[ToolType]:
        """Get the list of enabled tools.

        If no tools are explicitly enabled, all tools are enabled.

        Returns:
            List of enabled tool names

        """
        if not self.tools:
            return list(ToolType)
        return self.tools

    @property
    def server_metadata(self) -> dict[str, str]:
        """Get the server metadata for Smithery registry."""
        return {
            "name": "sequential-tools",
            "display_name": "Sequential Tools & Sequential Story",
            "version": "0.1.4",
            "description": "MCP tools for dynamic problem-solving through Sequential Thinking and Sequential Story",
            "author": "dhkts1",
            "repository": "https://github.com/dhkts1/sequentialStory",
            "documentation": "https://github.com/dhkts1/sequentialStory/blob/main/README.md",
        }


# Create a global instance of the settings
settings = Settings()


def get_settings() -> Settings:
    """Create and return a settings instance.

    Returns:
        Settings instance

    """
    return settings
