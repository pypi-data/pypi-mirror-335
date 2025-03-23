"""Server implementation for Sequential Tools."""

from mcp.server.fastmcp import FastMCP

from .sequential_story_processor import SequentialStoryProcessor
from .sequential_thinking_processor import SequentialThinkingProcessor
from .utils.settings import ToolType, get_settings

settings = get_settings()


class SequentialToolsServer:
    """Server for Sequential Tools including Sequential Story and Sequential Thinking tools."""

    def __init__(self) -> None:
        """Initialize the server with MCP components."""
        # Create the MCP server
        self.mcp = FastMCP(
            name=settings.server_metadata["name"],
            version=settings.server_metadata["version"],
            description=self._get_description(),
        )

        # Initialize and register enabled tools
        self._initialize_tools()

    def _get_description(self) -> str:
        """Generate appropriate description based on enabled tools."""
        enabled_tools = settings.enabled_tools
        thinking_enabled = ToolType.THINKING in enabled_tools
        story_enabled = ToolType.STORY in enabled_tools

        if thinking_enabled and story_enabled:
            return "Sequential Thinking and Sequential Story tools for MCP"
        if thinking_enabled:
            return "Sequential Thinking tool for MCP"
        if story_enabled:
            return "Sequential Story tool for MCP"
        return "Sequential Tools MCP Server (no tools enabled)"

    def _initialize_tools(self) -> None:
        """Initialize processors and register tools based on configuration."""
        enabled_tools = settings.enabled_tools
        # Initialize and register story tool if enabled
        if ToolType.STORY in enabled_tools:
            story_processor = SequentialStoryProcessor()
            story_processor.register_with_mcp(self.mcp)

        # Initialize and register thinking tool if enabled
        if ToolType.THINKING in enabled_tools:
            thinking_processor = SequentialThinkingProcessor()
            thinking_processor.register_with_mcp(self.mcp)

    def run(self) -> None:
        """Run the server with stdio transport."""
        self.mcp.run()


# For backward compatibility
SequentialStoryServer = SequentialToolsServer
