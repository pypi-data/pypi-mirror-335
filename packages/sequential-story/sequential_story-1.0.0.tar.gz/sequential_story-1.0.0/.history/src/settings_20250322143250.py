"""Configuration settings for Sequential Tools MCP Server.

This module provides a Pydantic Settings class for managing configuration
of the Sequential Tools MCP Server, with support for environment variables
and command-line arguments.
"""

from enum import Enum
from typing import ClassVar

from pydantic import field_validator
from pydantic_settings import BaseSettings


class ToolType(str, Enum):
    """Available tool types for Sequential Tools server."""

    STORY = "story"
    THINKING = "thinking"


class Settings(BaseSettings):
    """Settings for Sequential Tools MCP Server.

    Settings can be configured via environment variables with the prefix SEQUENTIAL_TOOLS_
    or via command-line arguments.
    """

    # Tool configuration
    enable: list[str] | None = None

    # List of all available tools
    AVAILABLE_TOOLS: ClassVar[list[str]] = [tool.value for tool in ToolType]

    # Server metadata
    name: str = "sequential-tools"
    display_name: str = "Sequential Tools & Sequential Story"
    version: str = "0.1.0"
    description: str = "MCP tools for dynamic problem-solving through Sequential Thinking and Sequential Story"
    author: str = "dhkts1"
    repository: str = "https://github.com/dhkts1/sequentialStory"
    documentation: str = "https://github.com/dhkts1/sequentialStory/README.md"

    @field_validator("enable")
    @classmethod
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
    def server_metadata(self) -> dict:
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
    def server_config(self) -> dict:
        """Get the server configuration dictionary."""
        enabled_tools = self.get_enabled_tools()
        return {"enabled_tools": enabled_tools} if enabled_tools else {}

    model_config = {
        "env_prefix": "SEQUENTIAL_TOOLS_",
        "extra": "ignore",
    }


def get_settings() -> Settings:
    """Create and return a settings instance.

    Returns:
        Settings instance

    """
    return Settings()
