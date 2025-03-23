"""Server implementation for Sequential Tools."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from .sequential_story_processor import SequentialStoryProcessor
from .sequential_thinking_processor import SequentialThinkingProcessor
from .utils.settings import settings


class SequentialToolsServer:
    """Server for Sequential Tools including Sequential Story and Sequential Thinking tools."""

    def __init__(self, metadata: dict[str, Any] | None = None, config: dict[str, Any] | None = None) -> None:
        """Initialize the server with MCP components.

        Args:
            metadata: Optional metadata dictionary with server information for Smithery.
            config: Optional configuration dictionary to control which tools are enabled.

        """
        # Get enabled tools from settings or provided config
        enabled_tools = (config or {}).get("enabled_tools", settings.get_enabled_tools())
        self.enabled_tools = set(enabled_tools)

        # Create the MCP server
        self.mcp = FastMCP(
            name=(metadata or settings.server_metadata).get("name", "sequential-tools-server"),
            version=(metadata or settings.server_metadata).get("version", "0.1.0"),
            description=self._get_description(),
        )

        # Initialize and register enabled tools
        self._initialize_tools()

    def _get_description(self) -> str:
        """Generate appropriate description based on enabled tools."""
        thinking_enabled = "thinking" in self.enabled_tools
        story_enabled = "story" in self.enabled_tools

        if thinking_enabled and story_enabled:
            return "Sequential Thinking and Sequential Story tools for MCP"
        if thinking_enabled:
            return "Sequential Thinking tool for MCP"
        if story_enabled:
            return "Sequential Story tool for MCP"
        return "Sequential Tools MCP Server (no tools enabled)"

    def _initialize_tools(self) -> None:
        """Initialize processors and register tools based on configuration."""
        # Initialize and register story tool if enabled
        if "story" in self.enabled_tools:
            story_processor = SequentialStoryProcessor()
            story_processor.register_with_mcp(self.mcp)

        # Initialize and register thinking tool if enabled
        if "thinking" in self.enabled_tools:
            thinking_processor = SequentialThinkingProcessor()
            thinking_processor.register_with_mcp(self.mcp)

    def run(self) -> None:
        """Run the server with stdio transport."""
        self.mcp.run()

    def get_enabled_tools(self) -> list[str]:
        """Return the list of enabled tools."""
        return list(self.enabled_tools)


# For backward compatibility
SequentialStoryServer = SequentialToolsServer
