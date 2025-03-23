"""Settings module for Sequential Tools MCP Server.

This module provides a flexible and type-safe way to manage application settings
for the Sequential Tools server, using Pydantic for configuration.
"""

from enum import StrEnum

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ToolType(StrEnum):
    """Available tool types for Sequential Tools server."""

    STORY = "story"
    THINKING = "thinking"


class Settings(BaseSettings):
    """Application settings for Sequential Tools MCP Server."""

    model_config = SettingsConfigDict(
        cli_parse_args=True,
        env_prefix="SEQUENTIAL_TOOLS_",
        env_nested_delimiter="__",
        extra="ignore",
        case_sensitive=False,
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
    DEBUG: bool = Field(
        default=False,
        description="Enable or disable debug mode.",
    )

    # Tool configuration
    tools: list[ToolType] = Field(
        default=[ToolType.THINKING, ToolType.STORY],
        description="List of tools to enable. If None, all tools are enabled.",
    )

    @field_validator("tools", mode="before")
    @classmethod
    def parse_tools_env(cls, value: list[ToolType] | ToolType | str | None) -> list[ToolType]:
        """Parse tools from environment variable or command line."""
        # If value is None, return all tools
        if value is None:
            return list(ToolType)

        # When a single string is passed (environment variable case)
        if isinstance(value, str):
            # Handle comma-separated values
            if "," in value:
                tools = []
                for tool_name in value.split(","):
                    tool_name = tool_name.strip().lower()
                    try:
                        tools.append(ToolType(tool_name))
                    except ValueError:
                        pass
                return tools if tools else list(ToolType)

            # Single value case
            try:
                return [ToolType(value.strip().lower())]
            except ValueError:
                return list(ToolType)

        # When a single ToolType is passed
        if isinstance(value, ToolType):
            return [value]

        # When a list is passed, it might already be converted to ToolType or still be strings
        if isinstance(value, list):
            if not value:  # Empty list case
                return list(ToolType)

            valid_tools = []
            for item in value:
                if isinstance(item, str):
                    try:
                        valid_tools.append(ToolType(item.strip().lower()))
                    except ValueError:
                        pass
                elif isinstance(item, ToolType):
                    valid_tools.append(item)
            return valid_tools if valid_tools else list(ToolType)

        # Default fallback for unexpected types
        return list(ToolType)

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
            "version": "0.1.0",
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
