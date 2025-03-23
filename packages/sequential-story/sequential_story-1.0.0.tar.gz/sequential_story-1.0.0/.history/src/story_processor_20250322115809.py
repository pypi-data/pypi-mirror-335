"""Implementation of the sequential story processor for mnemonic storytelling."""

from typing import Any

from pydantic import BaseModel
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


class StoryElementData(BaseModel):
    """Data structure for a story element in sequential storytelling."""

    element: str
    elementNumber: int
    totalElements: int
    nextElementNeeded: bool
    isRevision: bool | None = None
    revisesElement: int | None = None
    branchFromElement: int | None = None
    branchId: str | None = None
    needsMoreElements: bool | None = None
    # Story-specific fields
    character: str | None = None
    setting: str | None = None
    tone: str | None = None
    plotPoint: str | None = None


class ContentItem(BaseModel):
    """Structure for a content item in response."""

    type: str
    text: dict[str, Any] | str


class ProcessResult(BaseModel):
    """Structure for a process result."""

    content: list[ContentItem]
    isError: bool | None = None


class SequentialStoryProcessor:
    """Processor for sequential storytelling with mnemonic elements."""

    def __init__(self) -> None:
        """Initialize the story processor with empty history and branches."""
        self.element_history: list[StoryElementData] = []
        self.branches: dict[str, list[StoryElementData]] = {}
        self.console = Console(stderr=True)

    def validate_element_data(self, data: dict[str, Any]) -> StoryElementData:
        """Validate input data and convert to StoryElementData.

        Args:
            data: Input data to validate

        Returns:
            Validated data as StoryElementData object

        Raises:
            ValueError: If validation fails due to missing or invalid fields

        """
        try:
            # Use Pydantic's validation to directly create a model
            return StoryElementData.model_validate(data)
        except Exception as e:
            error_msg = f"Invalid data: {e}"
            raise ValueError(error_msg) from e

    def format_element(self, element_data: StoryElementData) -> Panel:
        """Format a story element for display.

        Args:
            element_data: The story element to format

        Returns:
            A rich Panel object for display

        """
        # Set up styling based on element type
        if element_data.isRevision:
            prefix = Text("🔄 Revision", style="yellow")
            context = f" (revising element {element_data.revisesElement})"
            style = "yellow"
        elif element_data.branchFromElement:
            prefix = Text("🌿 Branch", style="green")
            context = f" (from element {element_data.branchFromElement}, ID: {element_data.branchId})"
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
        if element_data.plotPoint:
            extra_context.append(f"Plot point: {element_data.plotPoint}")

        # Create header
        header = Text(f"{prefix} {element_data.elementNumber}/{element_data.totalElements}{context}")
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
            validated_input = self.validate_element_data(input_data)

            # Adjust total elements if needed
            if validated_input.elementNumber > validated_input.totalElements:
                validated_input.totalElements = validated_input.elementNumber

            # Add to history
            self.element_history.append(validated_input)

            # Handle branches
            if validated_input.branchFromElement and validated_input.branchId:
                if validated_input.branchId not in self.branches:
                    self.branches[validated_input.branchId] = []
                self.branches[validated_input.branchId].append(validated_input)

            # Display the formatted element
            self.console.print(self.format_element(validated_input))

            # Return result
            return ProcessResult(
                content=[
                    ContentItem(
                        type="text",
                        text={
                            "elementNumber": validated_input.elementNumber,
                            "totalElements": validated_input.totalElements,
                            "nextElementNeeded": validated_input.nextElementNeeded,
                            "branches": list(self.branches.keys()),
                            "elementHistoryLength": len(self.element_history),
                        },
                    )
                ]
            )
        except Exception as e:
            return ProcessResult(
                content=[
                    ContentItem(
                        type="text",
                        text={
                            "error": str(e),
                            "status": "failed",
                        },
                    )
                ],
                isError=True,
            )
