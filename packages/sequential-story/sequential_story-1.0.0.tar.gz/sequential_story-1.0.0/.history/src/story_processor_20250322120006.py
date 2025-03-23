"""Implementation of the sequential story processor for mnemonic storytelling."""

from typing import Any

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
    def adjust_total_elements(self) -> "StoryElementData":
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
    """Processor for sequential storytelling with mnemonic elements."""

    def __init__(self) -> None:
        """Initialize the story processor with empty history and branches."""
        self.element_history: list[StoryElementData] = []
        self.branches: dict[str, list[StoryElementData]] = {}
        self.console = Console(stderr=True)

    def format_element(self, element_data: StoryElementData) -> Panel:
        """Format a story element for display.

        Args:
            element_data: The story element to format

        Returns:
            A rich Panel object for display

        """
        # Set up styling based on element type
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

        # Add extra context for story-specific fields
        extra_context = []
        if element_data.character:
            extra_context.append(f"Character: {element_data.character}")
        if element_data.setting:
            extra_context.append(f"Setting: {element_data.setting}")
        if element_data.tone:
            extra_context.append(f"Tone: {element_data.tone}")
        if element_data.plot_point:
            extra_context.append(f"Plot point: {element_data.plot_point}")

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

    def process_element(self, input_data: dict[str, Any]) -> ProcessResult:
        """Process a new story element.

        Args:
            input_data: Input data for the story element

        Returns:
            Result of processing with content and optional error flag

        """
        try:
            # Let Pydantic handle validation automatically
            validated_input = StoryElementData.model_validate(input_data)

            # Add to history
            self.element_history.append(validated_input)

            # Handle branches
            if validated_input.branch_from_element and validated_input.branch_id:
                if validated_input.branch_id not in self.branches:
                    self.branches[validated_input.branch_id] = []
                self.branches[validated_input.branch_id].append(validated_input)

            # Display the formatted element
            self.console.print(self.format_element(validated_input))

            # Return result using factory method
            return ProcessResult.create_success(validated_input, list(self.branches.keys()), len(self.element_history))
        except Exception as e:
            return ProcessResult.create_error(e)
