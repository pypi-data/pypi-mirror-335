"""Settings module for Sequential Tools MCP Server.

This module provides a flexible and type-safe way to manage application settings
for the Sequential Tools server, using Pydantic for configuration.
"""

from enum import Enum
from typing import Any, ClassVar

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ToolType(str, Enum):
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
    enable: list[str] | None = Field(
        default=None,
        description="List of tools to enable. If None, all tools are enabled.",
    )

    # List of all available tools
    AVAILABLE_TOOLS: ClassVar[list[str]] = [tool.value for tool in ToolType]

    # Server metadata
    name: str = Field(
        default="sequential-tools",
        description="Server name for MCP registry",
    )
    display_name: str = Field(
        default="Sequential Tools & Sequential Story",
        description="Display name for MCP registry",
    )
    version: str = Field(
        default="0.1.0",
        description="Server version",
    )
    description: str = Field(
        default="MCP tools for dynamic problem-solving through Sequential Thinking and Sequential Story",
        description="Server description for MCP registry",
    )
    author: str = Field(
        default="dhkts1",
        description="Server author for MCP registry",
    )
    repository: str = Field(
        default="https://github.com/dhkts1/sequentialStory",
        description="Project repository URL",
    )
    documentation: str = Field(
        default="https://github.com/dhkts1/sequentialStory/README.md",
        description="Documentation URL",
    )

    @field_validator("enable")
    def validate_enabled_tools(cls, tools: list[str] | None) -> list[str] | None:
        """Validate that the enabled tools are in the list of available tools."""
        if tools is None:
            return None

        valid_tools = []
        for tool in tools:
            if tool in cls.AVAILABLE_TOOLS:
                valid_tools.append(tool)
            else:
                raise ValueError(f"Invalid tool: {tool}. Available tools are: {', '.join(cls.AVAILABLE_TOOLS)}")

        return valid_tools

    def get_enabled_tools(self) -> list[str]:
        """Get the list of enabled tools.

        If no tools are explicitly enabled, all tools are enabled.

        Returns:
            List of enabled tool names

        """
        if not self.enable:
            return self.AVAILABLE_TOOLS
        return self.enable

    @property
    def server_metadata(self) -> dict[str, str]:
        """Get the server metadata for Smithery registry."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "repository": self.repository,
            "documentation": self.documentation,
        }

    @property
    def server_config(self) -> dict[str, Any]:
        """Get the server configuration dictionary for SequentialToolsServer."""
        enabled_tools = self.get_enabled_tools()
        return {"enabled_tools": enabled_tools} if enabled_tools else {}

    model_config = SettingsConfigDict(
        env_prefix="SEQUENTIAL_TOOLS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Create a global instance of the settings
settings = Settings()


def get_settings() -> Settings:
    """Create and return a settings instance.

    Returns:
        Settings instance

    """
    return settings
