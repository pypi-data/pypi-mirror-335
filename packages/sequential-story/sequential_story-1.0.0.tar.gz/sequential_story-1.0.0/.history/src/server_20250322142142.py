"""Server implementation for Sequential Tools."""

from collections.abc import Callable
from typing import Any, TextIO

from mcp.server.fastmcp import FastMCP

from .sequential_story_processor import ProcessResult as StoryProcessResult
from .sequential_story_processor import SequentialStoryProcessor, StoryElementData
from .sequential_thinking_processor import ProcessResult as ThinkingProcessResult
from .sequential_thinking_processor import SequentialThinkingProcessor, SequentialThoughtData


class SequentialToolsServer:
    """Server for Sequential Tools including Sequential Story and Sequential Thinking tools."""

    def __init__(self, metadata: dict[str, Any] | None = None, config: dict[str, Any] | None = None) -> None:
        """Initialize the server with MCP components.

        Args:
            metadata: Optional metadata dictionary with server information for Smithery.
                     Expected fields: name, version, description, author, etc.
            config: Optional configuration dictionary to control which tools are enabled.
                    Available options:
                    - enabled_tools: List of tool names to enable. Options: ["story", "thinking"] or ["all"]
                    - disabled_tools: List of tool names to disable. Options: ["story", "thinking"] or []

        """
        # Use provided metadata or defaults
        meta = metadata or {}
        self.config = config or {}

        # Determine which tools should be enabled
        self.enabled_tools = self._resolve_enabled_tools()

        # Set up description based on enabled tools
        description = self._get_description_based_on_enabled_tools()

        self.mcp = FastMCP(
            name=meta.get("name", "sequential-tools-server"),
            version=meta.get("version", "0.1.0"),
            description=description,
        )

        # Initialize processors
        self.story_processor = None
        self.thinking_processor = None
        self.sequentialstory_tool = None
        self.sequentialthinking_tool = None

        # Initialize and register only the enabled tools
        self._initialize_enabled_processors()
        self._register_enabled_tools()

    def _resolve_enabled_tools(self) -> set[str]:
        """Determine which tools should be enabled based on configuration.

        Returns:
            Set of enabled tool names

        """
        all_tools = {"story", "thinking"}

        # First check if specific tools are enabled
        enabled_tools = set(self.config.get("enabled_tools", ["all"]))
        if "all" in enabled_tools:
            enabled_tools = all_tools.copy()

        # Then remove any explicitly disabled tools
        disabled_tools = set(self.config.get("disabled_tools", []))
        enabled_tools = enabled_tools - disabled_tools

        # Ensure at least one tool is enabled
        if not enabled_tools:
            # If no tools would be enabled, default to enabling all
            enabled_tools = all_tools

        return enabled_tools

    def _get_description_based_on_enabled_tools(self) -> str:
        """Generate appropriate description based on enabled tools.

        Returns:
            Description string for the MCP server

        """
        tools = []
        if "thinking" in self.enabled_tools:
            tools.append("Sequential Thinking")
        if "story" in self.enabled_tools:
            tools.append("Sequential Story")

        if len(tools) == 2:
            return f"{tools[0]} and {tools[1]} tools for MCP"
        return f"{tools[0]} tool for MCP"

    def _initialize_enabled_processors(self) -> None:
        """Initialize only the processors that are needed for enabled tools."""
        if "story" in self.enabled_tools:
            self.story_processor = SequentialStoryProcessor()

        if "thinking" in self.enabled_tools:
            self.thinking_processor = SequentialThinkingProcessor()

    def _register_enabled_tools(self) -> None:
        """Register only the tools that are enabled."""
        if "story" in self.enabled_tools:
            self.sequentialstory_tool = self.create_sequentialstory_tool()

        if "thinking" in self.enabled_tools:
            self.sequentialthinking_tool = self.create_sequentialthinking_tool()

    def create_sequentialstory_tool(self) -> Callable[[StoryElementData], StoryProcessResult]:
        """Create and register the Sequential Story tool.

        Returns:
            The registered tool callable

        """
        # Only create the tool if the processor is initialized
        if not self.story_processor:
            raise RuntimeError("Cannot create Sequential Story tool: story processor is not initialized")

        @self.mcp.tool(
            description="""A detailed tool for narrative-based problem-solving through Sequential Story.

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
        def sequentialstory(data: StoryElementData) -> StoryProcessResult:
            """Process a Sequential Story element.

            Args:
                data: The story element data

            Returns:
                The processing result

            """
            # Process the StoryElementData directly
            return self.story_processor.process_element(data)

        return sequentialstory

    def create_sequentialthinking_tool(self) -> Callable[[SequentialThoughtData], ThinkingProcessResult]:
        """Create and register the Sequential Thinking tool.

        Returns:
            The registered tool callable

        """
        # Only create the tool if the processor is initialized
        if not self.thinking_processor:
            raise RuntimeError("Cannot create Sequential Thinking tool: thinking processor is not initialized")

        @self.mcp.tool(
            description="""A detailed tool for dynamic and reflective problem-solving through Sequential Thinking.

        This tool helps analyze problems through a flexible thinking process that can adapt and evolve.
        Each thought can build on, question, or revise previous insights as understanding deepens.

        When to use this tool:
        - Breaking down complex problems into steps
        - Planning and design with room for revision
        - Analysis that might need course correction
        - Problems where the full scope might not be clear initially
        - Problems that require a multi-step solution
        - Tasks that need to maintain context over multiple steps
        - Situations where irrelevant information needs to be filtered out

        Key features:
        - You can adjust total_thoughts up or down as you progress
        - You can question or revise previous thoughts
        - You can add more thoughts even after reaching what seemed like the end
        - You can express uncertainty and explore alternative approaches
        - Not every thought needs to build linearly - you can branch or backtrack
        - Generates a solution hypothesis
        - Verifies the hypothesis based on the Chain of Thought steps
        - Repeats the process until satisfied
        - Provides a correct answer

        Parameters explained:
        - thought: Your current thinking step, which can include:
        * Regular analytical steps
        * Revisions of previous thoughts
        * Questions about previous decisions
        * Realizations about needing more analysis
        * Changes in approach
        * Hypothesis generation
        * Hypothesis verification
        - next_thought_needed: True if you need more thinking, even if at what seemed like the end
        - thought_number: Current number in sequence (can go beyond initial total if needed)
        - total_thoughts: Current estimate of thoughts needed (can be adjusted up/down)
        - is_revision: A boolean indicating if this thought revises previous thinking
        - revises_thought: If is_revision is true, which thought number is being reconsidered
        - branch_from_thought: If branching, which thought number is the branching point
        - branch_id: Identifier for the current branch (if any)
        - needs_more_thoughts: If reaching end but realizing more thoughts needed

        You should:
        1. Start with an initial estimate of needed thoughts, but be ready to adjust
        2. Feel free to question or revise previous thoughts
        3. Don't hesitate to add more thoughts if needed, even at the "end"
        4. Express uncertainty when present
        5. Mark thoughts that revise previous thinking or branch into new paths
        6. Ignore information that is irrelevant to the current step
        7. Generate a solution hypothesis when appropriate
        8. Verify the hypothesis based on the Chain of Thought steps
        9. Repeat the process until satisfied with the solution
        10. Provide a single, ideally correct answer as the final output
        11. Only set next_thought_needed to false when truly done and a satisfactory answer is reached"""
        )
        def sequentialthinking(data: SequentialThoughtData) -> ThinkingProcessResult:
            """Process a Sequential Thinking element.

            Args:
                data: The thought element data

            Returns:
                The processing result

            """
            # Process the SequentialThoughtData directly
            return self.thinking_processor.process_thought(data)

        return sequentialthinking

    def run(self) -> None:
        """Run the server with stdio transport."""
        # Run the MCP server - using run method instead of run_async
        self.mcp.run()
        enabled_tools_str = ", ".join(self.enabled_tools)
        print(
            f"Sequential Tools MCP Server running on stdio with enabled tools: {enabled_tools_str}",
            file=self.get_stderr(),
        )

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

    def get_enabled_tools(self) -> list[str]:
        """Return the list of enabled tools.

        Returns:
            List of enabled tool names

        """
        return list(self.enabled_tools)


# For backward compatibility
SequentialStoryServer = SequentialToolsServer
