"""Server implementation for the sequential story MCP tool."""

from typing import Any, TypeVar, cast

from .story_processor import SequentialStoryProcessor

# Type definitions for better type checking
T = TypeVar("T")
ResponseType = TypeVar("ResponseType")


# The classes below will need the modelcontextprotocol package to be installed
# These are placeholders that match the expected interface
class Server:
    """Placeholder for MCP Server implementation."""

    def __init__(self, server_info: dict[str, Any], capabilities: dict[str, Any]) -> None:
        """Initialize server with info and capabilities."""
        self.server_info = server_info
        self.capabilities = capabilities

    def set_request_handler(self, schema: Any, handler: Any) -> None:
        """Set a request handler for a schema."""

    async def connect(self, transport: Any) -> None:
        """Connect the server to a transport."""


class StdioServerTransport:
    """Placeholder for MCP StdioServerTransport implementation."""


class CallToolRequestSchema:
    """Placeholder for CallToolRequestSchema."""


class ListToolsRequestSchema:
    """Placeholder for ListToolsRequestSchema."""


# Type definition for the Tool
Tool = dict[str, Any]


# Define the Sequential Story Tool
SEQUENTIAL_STORY_TOOL: Tool = {
    "name": "sequentialstory",
    "description": """A detailed tool for narrative-based problem-solving through sequential storytelling.
This tool helps structure complex problems as story elements that build on each other.
Each element contributes to a coherent narrative that's easier to remember than abstract concepts.

When to use this tool:
- Breaking down complex problems into memorable story elements
- Creating mnemonic devices for better retention
- Developing ideas with narrative structure for easier recall
- Problem exploration that benefits from character, setting, and plot
- Tasks where memory enhancement is valuable
- Building coherent mental models through storytelling
- Creating knowledge frameworks that are easier to memorize

Key features:
- You can adjust total_elements count as your story develops
- You can revise previous elements when needed
- You can branch into alternative storylines
- You can incorporate characters, settings, tones, and plot points
- Not every element needs to follow linearly - you can branch or introduce new narrative paths
- Uses storytelling as a mnemonic technique to enhance retention
- Leverages narrative structure to make complex concepts more memorable

Parameters explained:
- element: Your current story element
- next_element_needed: True if the story should continue
- element_number: Current element number in sequence
- total_elements: Current estimate of elements needed
- is_revision: A boolean indicating if this revises a previous element
- revises_element: If is_revision is true, which element is being reconsidered
- branch_from_element: If branching, which element number is the branching point
- branch_id: Identifier for the current branch
- needs_more_elements: If reaching end but realizing more elements needed
- character: Optional character involved in this element
- setting: Optional setting for this element
- tone: Optional emotional tone of this element
- plot_point: Optional plot development in this element

You should:
1. Start with an initial estimate of needed elements, but be ready to adjust
2. Use narrative structure to enhance memorability
3. Incorporate story elements like characters and settings to make concepts more tangible
4. Revise elements when needed to refine the narrative
5. Branch into alternative storylines when exploring different possibilities
6. Use mnemonic techniques to make your story more memorable
7. Only set next_element_needed to false when the story is complete""",
    "inputSchema": {
        "type": "object",
        "properties": {
            "element": {"type": "string", "description": "Your current story element"},
            "nextElementNeeded": {"type": "boolean", "description": "Whether another story element is needed"},
            "elementNumber": {"type": "integer", "description": "Current element number", "minimum": 1},
            "totalElements": {"type": "integer", "description": "Estimated total elements needed", "minimum": 1},
            "isRevision": {"type": "boolean", "description": "Whether this revises a previous element"},
            "revisesElement": {"type": "integer", "description": "Which element is being reconsidered", "minimum": 1},
            "branchFromElement": {"type": "integer", "description": "Branching point element number", "minimum": 1},
            "branchId": {"type": "string", "description": "Branch identifier"},
            "needsMoreElements": {"type": "boolean", "description": "If more elements are needed"},
            "character": {"type": "string", "description": "Character involved in this element"},
            "setting": {"type": "string", "description": "Setting for this element"},
            "tone": {"type": "string", "description": "Emotional tone of this element"},
            "plotPoint": {"type": "string", "description": "Plot development in this element"},
        },
        "required": ["element", "nextElementNeeded", "elementNumber", "totalElements"],
    },
}


class RequestParams:
    """Placeholder for request params structure."""

    def __init__(self) -> None:
        """Initialize the request params."""
        self.name = ""
        self.arguments = {}


class Request:
    """Placeholder for request structure."""

    def __init__(self) -> None:
        """Initialize the request object."""
        self.params = RequestParams()


class SequentialStoryServer:
    """Server for the Sequential Story MCP tool."""

    def __init__(self) -> None:
        """Initialize the server with MCP components."""
        self.server = Server(
            {
                "name": "sequential-story-server",
                "version": "0.1.0",
            },
            {
                "capabilities": {
                    "tools": {},
                },
            },
        )

        self.story_processor = SequentialStoryProcessor()

        # Set up request handlers
        self.server.set_request_handler(ListToolsRequestSchema, self._handle_list_tools)

        self.server.set_request_handler(CallToolRequestSchema, self._handle_call_tool)

    async def _handle_list_tools(self, _: object) -> dict[str, list[Tool]]:
        """Handle tool listing requests.

        Args:
            _: Unused request parameter

        Returns:
            Dict with available tools

        """
        return {"tools": [SEQUENTIAL_STORY_TOOL]}

    async def _handle_call_tool(self, request: Request) -> dict[str, Any]:
        """Handle tool call requests.

        Args:
            request: Tool call request

        Returns:
            Result of tool processing

        """
        if request.params.name == "sequentialstory":
            result = self.story_processor.process_element(request.params.arguments)
            return cast("dict[str, Any]", result)

        return {"content": [{"type": "text", "text": f"Unknown tool: {request.params.name}"}], "isError": True}

    async def run(self) -> None:
        """Run the server with stdio transport."""
        transport = StdioServerTransport()
        await self.server.connect(transport)
        print("Sequential Story MCP Server running on stdio", file=import_sys())


def import_sys() -> Any:
    """Import sys module and return stderr.

    Returns:
        sys.stderr for printing messages

    """
    import sys

    return sys.stderr
