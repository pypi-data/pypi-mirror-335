"""Server implementation for the sequential story MCP tool."""

from collections.abc import Callable
from typing import TextIO

from mcp.server.fastmcp import FastMCP

from .story_processor import ProcessResult, SequentialStoryProcessor, StoryElementData


class SequentialStoryServer:
    """Server for the Sequential Story MCP tool."""

    def __init__(self) -> None:
        """Initialize the server with MCP components."""
        self.mcp = FastMCP(
            name="sequential-story-server",
            version="0.1.0",
        )

        self.story_processor = SequentialStoryProcessor()

        # Register the sequential story tool
        self.sequentialstory_tool = self.create_sequentialstory_tool()

    def create_sequentialstory_tool(self) -> Callable[[StoryElementData], ProcessResult]:
        """Create and register the sequential story tool.

        Returns:
            The registered tool callable

        """

        @self.mcp.tool(
            description="""A detailed tool for narrative-based problem-solving through sequential storytelling.
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
7. Only set next_element_needed to false when the story is complete"""
        )
        def sequentialstory(data: StoryElementData) -> ProcessResult:
            """Process a sequential story element.

            Args:
                data: The story element data

            Returns:
                The processing result

            """
            # Process the StoryElementData directly
            return self.story_processor.process_element(data)

        return sequentialstory

    def run(self) -> None:
        """Run the server with stdio transport."""
        # Run the MCP server - using run method instead of run_async
        self.mcp.run()
        print("Sequential Story MCP Server running on stdio", file=self.get_stderr())

    def get_stderr(self) -> TextIO:
        """Get the stderr stream for logging.

        Returns:
            sys.stderr for printing messages

        """
        import sys

        return sys.stderr

    def _import_sys(self) -> TextIO:
        """Import sys module and return stderr.

        Returns:
            sys.stderr for printing messages

        """
        # Deprecated: use get_stderr() instead
        return self.get_stderr()
