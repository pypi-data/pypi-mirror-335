"""Implementation of the sequential thinking processor for analytical problem-solving."""

from typing import Any, Self

from pydantic import BaseModel, model_validator
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


class SequentialThoughtData(BaseModel):
    """Data structure for a thought element in sequential thinking."""

    thought: str
    thought_number: int
    total_thoughts: int
    next_thought_needed: bool
    is_revision: bool | None = None
    revises_thought: int | None = None
    branch_from_thought: int | None = None
    branch_id: str | None = None
    needs_more_thoughts: bool | None = None

    @model_validator(mode="after")
    def adjust_total_thoughts(self) -> Self:
        """Automatically adjust total thoughts if needed.

        Returns:
            Self with potentially adjusted total_thoughts

        """
        if self.thought_number > self.total_thoughts:
            self.total_thoughts = self.thought_number
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
    def create_success(cls, data: SequentialThoughtData, branches: list[str], history_length: int) -> "ProcessResult":
        """Create a success result.

        Args:
            data: The validated thought data
            branches: List of branch IDs
            history_length: Length of the thought history

        Returns:
            A new ProcessResult with success data

        """
        return cls(
            content=[
                ContentItem(
                    type="text",
                    text={
                        "thought_number": data.thought_number,
                        "total_thoughts": data.total_thoughts,
                        "next_thought_needed": data.next_thought_needed,
                        "needs_more_thoughts": data.needs_more_thoughts,
                        "branches": branches,
                        "thought_history_length": history_length,
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


class SequentialThinkingProcessor:
    """Processor for sequential thinking with analytical elements.

    This class manages a sequence of thought elements, handling the flow and structure
    of an analytical process that may include branches, revisions, and multiple thought paths.

    Flow Overview:
    1. Thoughts are submitted to the processor in sequence via the process_thought method
    2. Each thought is added to the thought_history and processed according to its type:
       - Standard thoughts are added to the main thought line
       - Branch thoughts (with branch_from_thought and branch_id) create or extend branches
       - Revision thoughts (with is_revision flag) modify existing thoughts
    3. The processor tracks thinking completion using two key flags:
       - next_thought_needed: Indicates if another thought should follow immediately
       - needs_more_thoughts: Determines if the thought branch/path is conceptually complete
    4. Thoughts are visually formatted with appropriate styling based on their type
    5. The processor can determine if a thinking process is complete by checking:
       - If the main thought line is complete
       - If all branches are complete

    Branching:
    - Thought elements can branch from any previous thought by specifying branch_from_thought
    - Each branch has a unique branch_id and maintains its own sequential flow
    - Branches are tracked separately from the main thought line but contribute to overall
      completion status

    Thinking Completion:
    - A thinking process with no elements is considered incomplete
    - A thinking process is only considered complete when both:
      1. The main thought line is complete (last element has needs_more_thoughts=False)
      2. All branches are complete (last element of each branch has needs_more_thoughts=False)
    - Visual indicators show when elements or the overall process need more content

    Formatting and Display:
    - Thoughts are displayed with styling based on their type (main line, revision, branch)
    - Context information shows thought relationships
    - Visual indicators highlight when more thoughts are needed

    This processor is designed to support analytical problem-solving techniques where
    thought elements build on each other in a structured, sequential manner.
    """

    def __init__(self) -> None:
        """Initialize the thinking processor with empty history and branches."""
        self.thought_history: list[SequentialThoughtData] = []
        self.branches: dict[str, list[SequentialThoughtData]] = {}
        self.console = Console(stderr=True)
        self.thinking_needs_more_thoughts: bool = True

    def _get_thought_style(self, thought_data: SequentialThoughtData) -> tuple[Text, str, str]:
        """Get the styling information for a thought.

        Args:
            thought_data: The thought element

        Returns:
            A tuple of (prefix text, context string, style string)

        """
        if thought_data.is_revision:
            prefix = Text("🔄 Revision", style="yellow")
            context = f" (revising thought {thought_data.revises_thought})"
            style = "yellow"
        elif thought_data.branch_from_thought:
            prefix = Text("🌿 Branch", style="green")
            context = f" (from thought {thought_data.branch_from_thought}, ID: {thought_data.branch_id})"
            style = "green"
        else:
            prefix = Text("💭 Thought", style="blue")
            context = ""
            style = "blue"

        return prefix, context, style

    def _get_extra_context(self, thought_data: SequentialThoughtData) -> list[str]:
        """Get extra context information for a thought element.

        Args:
            thought_data: The thought element

        Returns:
            A list of extra context strings

        """
        extra_context = []

        # Add needs_more_thoughts indicator if present
        if thought_data.needs_more_thoughts:
            extra_context.append("⚠️ Thinking process needs more thoughts")

        return extra_context

    def _check_element_needs_more(self, element_list: list[SequentialThoughtData]) -> bool:
        """Check if the last element in a list needs more thoughts.

        Args:
            element_list: List of thought elements

        Returns:
            True if the last element needs more thoughts, False otherwise

        """
        return bool(element_list and element_list[-1].needs_more_thoughts)

    def _get_main_thought_elements(self) -> list[SequentialThoughtData]:
        """Get elements that are part of the main thought line (not in branches).

        Returns:
            List of elements in the main thought line

        """
        return [e for e in self.thought_history if not e.branch_id]

    def _check_main_thought_complete(self) -> bool:
        """Check if the main thought line is complete.

        Returns:
            True if the main thought line is complete, False otherwise

        """
        main_elements = self._get_main_thought_elements()
        return not self._check_element_needs_more(main_elements)

    def _check_all_branches_complete(self) -> bool:
        """Check if all branches are complete.

        Returns:
            True if all branches are complete, False otherwise

        """
        return all(not self._check_element_needs_more(branch_elements) for branch_elements in self.branches.values())

    def is_thinking_complete(self) -> bool:
        """Check if the thinking process is complete.

        This is determined by looking at the needs_more_thoughts flag
        of the most recent elements in all branches.

        Returns:
            True if the thinking process is complete, False otherwise

        """
        # Thinking is incomplete if there are no elements
        if not self.thought_history:
            return False

        # Thinking is complete only if both main thought line and all branches are complete
        return self._check_main_thought_complete() and self._check_all_branches_complete()

    def format_thought(self, thought_data: SequentialThoughtData) -> Panel:
        """Format a thought element for display.

        Args:
            thought_data: The thought element to format

        Returns:
            A rich Panel object for display

        """
        # Get style information
        prefix, context, style = self._get_thought_style(thought_data)

        # Get extra context
        extra_context = self._get_extra_context(thought_data)

        # Create header
        header = Text(f"{prefix} {thought_data.thought_number}/{thought_data.total_thoughts}{context}")
        if extra_context:
            header.append("\n" + ", ".join(extra_context))

        # Create panel
        return Panel(
            Text(thought_data.thought),
            title=header,
            border_style=style,
        )

    def _handle_branch(self, element: SequentialThoughtData) -> None:
        """Handle branch-related processing for an element.

        Args:
            element: The thought element

        """
        if element.branch_from_thought and element.branch_id:
            if element.branch_id not in self.branches:
                self.branches[element.branch_id] = []
            self.branches[element.branch_id].append(element)

    def process_thought(self, element: SequentialThoughtData) -> ProcessResult:
        """Process a thought element.

        Args:
            element: The thought element data

        Returns:
            Result of processing

        """
        try:
            # Add to history
            self.thought_history.append(element)

            # Update thinking completion status
            if element.needs_more_thoughts is not None:
                self.thinking_needs_more_thoughts = element.needs_more_thoughts

            # Handle branches
            self._handle_branch(element)

            # Display the formatted element
            self.console.print(self.format_thought(element))

            # Display thinking completion status
            if not self.is_thinking_complete():
                self.console.print("Note: Thinking process is not yet complete", style="bold yellow")

            # Return result using factory method
            return ProcessResult.create_success(element, list(self.branches.keys()), len(self.thought_history))
        except Exception as e:
            return ProcessResult.create_error(e)
