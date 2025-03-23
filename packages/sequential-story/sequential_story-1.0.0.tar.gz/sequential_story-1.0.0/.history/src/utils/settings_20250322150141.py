"""Settings module for Sequential Tools MCP Server.

This module provides a flexible and type-safe way to manage application settings
for the Sequential Tools server, using Pydantic for configuration.
"""

from typing import Any, ClassVar

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class ToolType(strEnum):
    """Available tool types for Sequential Tools server."""

    STORY = "story"
    THINKING = "thinking"


class Settings(BaseSettings):
    """Application settings for Sequential Tools MCP Server.

    Provides a centralized configuration with environment variable support.
    Settings can be configured via environment variables with the prefix SEQUENTIAL_TOOLS_
    or via command-line arguments.
    """

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
    tools: list[ToolType] | None = Field(
        default=None,
        description="List of tools to enable. If None, all tools are enabled.",
    )

    # List of all available tools
    AVAILABLE_TOOLS: ClassVar[list[str]] = [tool.value for tool in ToolType]

    @field_validator("tools")
    @classmethod
    def validate_enabled_tools(cls, tools: list[str] | None) -> list[str]:
        """Validate that the enabled tools are in the list of available tools."""
        if tools is None:
            return cls.AVAILABLE_TOOLS

        valid_tools = []
        for tool in tools:
            if tool in cls.AVAILABLE_TOOLS:
                valid_tools.append(tool)
            else:
                msg = f"Invalid tool: {tool}. Available tools are: {', '.join(cls.AVAILABLE_TOOLS)}"
                raise ValueError(msg)

        return valid_tools

    def get_enabled_tools(self) -> list[str]:
        """Get the list of enabled tools.

        If no tools are explicitly enabled, all tools are enabled.

        Returns:
            List of enabled tool names

        """
        if not self.tools:
            return self.AVAILABLE_TOOLS
        return [tool.value for tool in self.tools]

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

    @property
    def server_config(self) -> dict[str, Any]:
        """Get the server configuration dictionary for SequentialToolsServer."""
        enabled_tools = self.get_enabled_tools()
        return {"enabled_tools": enabled_tools} if enabled_tools else {}


# Create a global instance of the settings
settings = Settings()


def get_settings() -> Settings:
    """Create and return a settings instance.

    Returns:
        Settings instance

    """
    return settings
