"""Implementation of the sequential story processor for mnemonic storytelling."""

from collections.abc import Callable
from typing import Any, Self

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, field_validator, model_validator
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


class StoryElementData(BaseModel):
    """Data structure for a story element in sequential storytelling."""

    element: str
    element_number: int
    total_elements: int
    next_element_needed: bool
    is_revision: bool | None = None
    revises_element: int | None = None
    branch_from_element: int | None = None
    branch_id: str | None = None
    needs_more_elements: bool | None = None
    # Story-specific fields
    character: str | None = None
    setting: str | None = None
    tone: str | None = None
    plot_point: str | None = None

    @field_validator("element")
    @classmethod
    def validate_element_not_empty(cls, v: str) -> str:
        """Validate that element is not empty.

        Args:
            v: The element value

        Returns:
            The validated element value

        Raises:
            ValueError: If element is empty

        """
        if not v.strip():
            msg = "Story element cannot be empty"
            raise ValueError(msg)
        return v

    @field_validator("element_number", "total_elements")
    @classmethod
    def validate_positive_numbers(cls, v: int) -> int:
        """Validate that number fields are positive.

        Args:
            v: The number value

        Returns:
            The validated number value

        Raises:
            ValueError: If number is not positive

        """
        if v <= 0:
            msg = "Number values must be positive"
            raise ValueError(msg)
        return v

    @model_validator(mode="after")
    def validate_branch_id(self) -> Self:
        """Validate branch_id is set when branch_from_element is set.

        Returns:
            Self with validated branch_id and branch_from_element

        Raises:
            ValueError: If branch_from_element is set but branch_id is not

        """
        if self.branch_from_element is not None and self.branch_id is None:
            msg = "branch_id must be set when branch_from_element is set"
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def validate_revision_element(self) -> Self:
        """Validate revises_element is set when is_revision is True.

        Returns:
            Self with validated is_revision and revises_element

        Raises:
            ValueError: If is_revision is True but revises_element is not set

        """
        if self.is_revision and self.revises_element is None:
            msg = "revises_element must be set when is_revision is True"
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def adjust_total_elements(self) -> Self:
        """Automatically adjust total elements if needed.

        Returns:
            Self with potentially adjusted total_elements

        """
        if self.element_number > self.total_elements:
            self.total_elements = self.element_number
        return self


class ContentItem(BaseModel):
    """Structure for a content item in response."""

    type: str
    text: dict[str, Any] | str


class ProcessResult(BaseModel):
    """Structure for a process result."""

    content: list[ContentItem]
    is_error: bool | None = None

    @classmethod
    def create_success(cls, data: StoryElementData, branches: list[str], history_length: int) -> "ProcessResult":
        """Create a success result.

        Args:
            data: The validated story element data
            branches: List of branch IDs
            history_length: Length of the element history

        Returns:
            A new ProcessResult with success data

        """
        return cls(
            content=[
                ContentItem(
                    type="text",
                    text={
                        "element_number": data.element_number,
                        "total_elements": data.total_elements,
                        "next_element_needed": data.next_element_needed,
                        "needs_more_elements": data.needs_more_elements,
                        "branches": branches,
                        "element_history_length": history_length,
                    },
                )
            ]
        )

    @classmethod
    def create_error(cls, error: Exception) -> "ProcessResult":
        """Create an error result.

        Args:
            error: The exception that occurred

        Returns:
            A new ProcessResult with error data

        """
        return cls(
            content=[
                ContentItem(
                    type="text",
                    text={
                        "error": str(error),
                        "status": "failed",
                    },
                )
            ],
            is_error=True,
        )


class SequentialStoryProcessor:
    """Processor for sequential storytelling with mnemonic elements.

    This class manages a sequence of story elements, handling the flow and structure
    of a narrative that may include branches, revisions, and multiple storylines.

    Flow Overview:
    1. Elements are submitted to the processor in sequence via the process_element method
    2. Each element is added to the element_history and processed according to its type:
       - Standard elements are added to the main story line
       - Branch elements (with branch_from_element and branch_id) create or extend branches
       - Revision elements (with is_revision flag) modify existing elements
    3. The processor tracks story completion using two key flags:
       - next_element_needed: Indicates if another element should follow immediately
       - needs_more_elements: Determines if the story branch/path is conceptually complete
    4. Elements are visually formatted with appropriate styling based on their type
    5. The processor can determine if a story is complete by checking:
       - If the main storyline is complete
       - If all branches are complete

    Branching:
    - Story elements can branch from any previous element by specifying branch_from_element
    - Each branch has a unique branch_id and maintains its own sequential flow
    - Branches are tracked separately from the main storyline but contribute to overall
      story completion status

    Story Completion:
    - A story with no elements is considered incomplete
    - A story is only considered complete when both:
      1. The main story line is complete (last element has needs_more_elements=False)
      2. All branches are complete (last element of each branch has needs_more_elements=False)
    - Visual indicators show when elements or the overall story need more content

    Formatting and Display:
    - Elements are displayed with styling based on their type (main story, revision, branch)
    - Context information shows element relationships and story-specific metadata
    - Visual indicators highlight when more elements are needed

    This processor is designed to support mnemonic storytelling techniques where
    narrative elements build on each other in a structured, sequential manner.
    """

    def __init__(self) -> None:
        """Initialize the story processor with empty history and branches."""
        self.element_history: list[StoryElementData] = []
        self.branches: dict[str, list[StoryElementData]] = {}
        self.console = Console(stderr=True)
        self.story_needs_more_elements: bool = True

    def _get_element_style(self, element_data: StoryElementData) -> tuple[Text, str, str]:
        """Get the styling information for an element.

        Args:
            element_data: The story element

        Returns:
            A tuple of (prefix text, context string, style string)

        """
        if element_data.is_revision:
            prefix = Text("🔄 Revision", style="yellow")
            context = f" (revising element {element_data.revises_element})"
            style = "yellow"
        elif element_data.branch_from_element:
            prefix = Text("🌿 Branch", style="green")
            context = f" (from element {element_data.branch_from_element}, ID: {element_data.branch_id})"
            style = "green"
        else:
            prefix = Text("📖 Story", style="blue")
            context = ""
            style = "blue"

        return prefix, context, style

    def _get_story_context(self, element_data: StoryElementData) -> list[str]:
        """Get story-specific context information for an element.

        Args:
            element_data: The story element

        Returns:
            A list of story context strings

        """
        context = []
        if element_data.character:
            context.append(f"Character: {element_data.character}")
        if element_data.setting:
            context.append(f"Setting: {element_data.setting}")
        if element_data.tone:
            context.append(f"Tone: {element_data.tone}")
        if element_data.plot_point:
            context.append(f"Plot point: {element_data.plot_point}")
        return context

    def _get_extra_context(self, element_data: StoryElementData) -> list[str]:
        """Get extra context information for a story element.

        Args:
            element_data: The story element

        Returns:
            A list of extra context strings

        """
        # Get story-specific context
        extra_context = self._get_story_context(element_data)

        # Add needs_more_elements indicator if present
        if element_data.needs_more_elements:
            extra_context.append("⚠️ Story needs more elements")

        return extra_context

    def _check_element_needs_more(self, element_list: list[StoryElementData]) -> bool:
        """Check if the last element in a list needs more elements.

        Args:
            element_list: List of story elements

        Returns:
            True if the last element needs more elements, False otherwise

        """
        return bool(element_list and element_list[-1].needs_more_elements)

    def _get_main_story_elements(self) -> list[StoryElementData]:
        """Get elements that are part of the main story line (not in branches).

        Returns:
            List of elements in the main story line

        """
        return [e for e in self.element_history if not e.branch_id]

    def _check_main_story_complete(self) -> bool:
        """Check if the main story line is complete.

        Returns:
            True if the main story is complete, False otherwise

        """
        main_elements = self._get_main_story_elements()
        return not self._check_element_needs_more(main_elements)

    def _check_all_branches_complete(self) -> bool:
        """Check if all branches are complete.

        Returns:
            True if all branches are complete, False otherwise

        """
        return all(not self._check_element_needs_more(branch_elements) for branch_elements in self.branches.values())

    def is_story_complete(self) -> bool:
        """Check if the story is complete.

        This is determined by looking at the needs_more_elements flag
        of the most recent elements in all branches.

        Returns:
            True if the story is complete, False otherwise

        """
        # Story is incomplete if there are no elements
        if not self.element_history:
            return False

        # Story is complete only if both main story and all branches are complete
        return self._check_main_story_complete() and self._check_all_branches_complete()

    def format_element(self, element_data: StoryElementData) -> Panel:
        """Format a story element for display.

        Args:
            element_data: The story element to format

        Returns:
            A rich Panel object for display

        """
        # Get style information
        prefix, context, style = self._get_element_style(element_data)

        # Get extra context
        extra_context = self._get_extra_context(element_data)

        # Create header
        header = Text(f"{prefix} {element_data.element_number}/{element_data.total_elements}{context}")
        if extra_context:
            header.append("\n" + ", ".join(extra_context))

        # Create panel
        return Panel(
            Text(element_data.element),
            title=header,
            border_style=style,
        )

    def _validate_element_references(self, element: StoryElementData) -> ValueError | None:
        """Validate that element references point to existing elements.

        Args:
            element: The story element to validate

        Returns:
            ValueError if references are invalid, None otherwise

        """
        # Check revision references
        if element.revises_element is not None:
            if element.revises_element <= 0:
                msg = f"revises_element {element.revises_element} must be positive"
                return ValueError(msg)
            if element.revises_element > len(self.element_history):
                msg = f"revises_element {element.revises_element} does not refer to an existing element"
                return ValueError(msg)

        # Check branch references
        if element.branch_from_element is not None:
            if element.branch_from_element <= 0:
                msg = f"branch_from_element {element.branch_from_element} must be positive"
                return ValueError(msg)
            if element.branch_from_element > len(self.element_history):
                msg = f"branch_from_element {element.branch_from_element} does not refer to an existing element"
                return ValueError(msg)

        return None

    def _display_element(self, element: StoryElementData) -> None:
        """Display a formatted element and story completion status.

        Args:
            element: The story element to display

        """
        self.console.print(self.format_element(element))

        if not self.is_story_complete():
            self.console.print("Note: Story is not yet complete", style="bold yellow")

    def _update_state(self, element: StoryElementData) -> None:
        """Update the processor state with a new element.

        Args:
            element: The story element to process

        """
        # Add to history
        self.element_history.append(element)

        # Update story completion status
        if element.needs_more_elements is not None:
            self.story_needs_more_elements = element.needs_more_elements

        # Handle branches
        self._handle_branch(element)

    def _handle_branch(self, element: StoryElementData) -> None:
        """Handle branch-related processing for an element.

        Args:
            element: The story element

        """
        if element.branch_from_element and element.branch_id:
            if element.branch_id not in self.branches:
                self.branches[element.branch_id] = []
            self.branches[element.branch_id].append(element)

    def process_element(self, element: StoryElementData) -> ProcessResult:
        """Process a story element.

        Args:
            element: The story element data

        Returns:
            Result of processing

        """
        try:
            # Validate references
            validation_error = self._validate_element_references(element)
            if validation_error:
                return ProcessResult.create_error(validation_error)

            # Update state
            self._update_state(element)

            # Display element
            self._display_element(element)

            # Return success result
            return ProcessResult.create_success(element, list(self.branches.keys()), len(self.element_history))
        except ValueError as e:
            # Handle expected validation errors
            return ProcessResult.create_error(e)
        except Exception as e:
            # Handle unexpected runtime errors
            return ProcessResult.create_error(e)

    def register_with_mcp(self, mcp: FastMCP) -> Callable[[StoryElementData], ProcessResult]:
        """Register the Sequential Story tool with an MCP server.

        Args:
            mcp: The MCP server to register with

        Returns:
            The registered tool function

        """

        @mcp.tool(
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
        def sequentialstory(data: StoryElementData) -> ProcessResult:
            """Process a Sequential Story element."""
            return self.process_element(data)

        return sequentialstory
