"""Implementation of the sequential story processor for mnemonic storytelling."""

from typing import Any, Self

from pydantic import BaseModel, model_validator
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
            # Add to history
            self.element_history.append(element)

            # Update story completion status
            if element.needs_more_elements is not None:
                self.story_needs_more_elements = element.needs_more_elements

            # Handle branches
            self._handle_branch(element)

            # Display the formatted element
            self.console.print(self.format_element(element))

            # Display story completion status
            if not self.is_story_complete():
                self.console.print("Note: Story is not yet complete", style="bold yellow")

            # Return result using factory method
            return ProcessResult.create_success(element, list(self.branches.keys()), len(self.element_history))
        except Exception as e:
            return ProcessResult.create_error(e)
