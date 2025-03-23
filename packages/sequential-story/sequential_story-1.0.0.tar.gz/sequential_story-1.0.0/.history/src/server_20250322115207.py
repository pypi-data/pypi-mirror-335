"""Server implementation for the sequential story MCP tool."""

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from .story_processor import ProcessResult, SequentialStoryProcessor


# Input model for the sequential story tool
class SequentialStoryInput(BaseModel):
    """Input model for the sequential story tool."""

    element: str
    elementNumber: int
    totalElements: int
    nextElementNeeded: bool
    isRevision: bool | None = None
    revisesElement: int | None = None
    branchFromElement: int | None = None
    branchId: str | None = None
    needsMoreElements: bool | None = None
    character: str | None = None
    setting: str | None = None
    tone: str | None = None
    plotPoint: str | None = None


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
- nextElementNeeded: True if the story should continue
- elementNumber: Current element number in sequence
- totalElements: Current estimate of elements needed
- isRevision: A boolean indicating if this revises a previous element
- revisesElement: If isRevision is true, which element is being reconsidered
- branchFromElement: If branching, which element number is the branching point
- branchId: Identifier for the current branch
- needsMoreElements: If reaching end but realizing more elements needed
- character: Optional character involved in this element
- setting: Optional setting for this element
- tone: Optional emotional tone of this element
- plotPoint: Optional plot development in this element

You should:
1. Start with an initial estimate of needed elements, but be ready to adjust
2. Use narrative structure to enhance memorability
3. Incorporate story elements like characters and settings to make concepts more tangible
4. Revise elements when needed to refine the narrative
5. Branch into alternative storylines when exploring different possibilities
6. Use mnemonic techniques to make your story more memorable
7. Only set nextElementNeeded to false when the story is complete"""
        )
        def sequentialstory(data: SequentialStoryInput) -> ProcessResult:
            """Process a sequential story element.

            Args:
                data: The story element data

            Returns:
                The processing result

            """
            # Convert Pydantic model to dict for compatibility with the processor
            input_dict = data.model_dump()
            result = self.story_processor.process_element(input_dict)
            return result

    async def run(self) -> None:
        """Run the server with stdio transport."""
        await self.mcp.run_stdio()
        print("Sequential Story MCP Server running on stdio", file=self._import_sys())

    def _import_sys(self):
        """Import sys module and return stderr.

        Returns:
            sys.stderr for printing messages

        """
        import sys

        return sys.stderr
