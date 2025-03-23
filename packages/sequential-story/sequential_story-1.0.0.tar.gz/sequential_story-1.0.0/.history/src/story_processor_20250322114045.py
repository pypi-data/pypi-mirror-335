"""Implementation of the sequential story processor for mnemonic storytelling."""

from dataclasses import dataclass
from typing import Any, TypedDict

from rich.console import Console
from rich.panel import Panel
from rich.text import Text


@dataclass
class StoryElementData:
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


class ContentItem(TypedDict):
    """Dictionary structure for a content item in response."""

    type: str
    text: str | dict[str, Any]


class ProcessResult(TypedDict, total=False):
    """Dictionary structure for a process result."""

    content: list[ContentItem]
    isError: bool


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
            TypeError: If data is not a dictionary or field types are incorrect
            ValueError: If required fields are missing

        """
        # Check required fields
        required_fields = ["element", "elementNumber", "totalElements", "nextElementNeeded"]
        for field in required_fields:
            if field not in data:
                missing_field_msg = f"Missing required field: {field}"
                raise ValueError(missing_field_msg)

        # Validate types of required fields
        if not isinstance(data["element"], str):
            element_type_msg = "element must be a string"
            raise TypeError(element_type_msg)

        if not isinstance(data["elementNumber"], int):
            element_number_type_msg = "elementNumber must be an integer"
            raise TypeError(element_number_type_msg)

        if not isinstance(data["totalElements"], int):
            total_elements_type_msg = "totalElements must be an integer"
            raise TypeError(total_elements_type_msg)

        if not isinstance(data["nextElementNeeded"], bool):
            next_element_type_msg = "nextElementNeeded must be a boolean"
            raise TypeError(next_element_type_msg)

        # Create StoryElementData object
        return StoryElementData(
            element=data["element"],
            element_number=data["elementNumber"],
            total_elements=data["totalElements"],
            next_element_needed=data["nextElementNeeded"],
            is_revision=data.get("isRevision"),
            revises_element=data.get("revisesElement"),
            branch_from_element=data.get("branchFromElement"),
            branch_id=data.get("branchId"),
            needs_more_elements=data.get("needsMoreElements"),
            character=data.get("character"),
            setting=data.get("setting"),
            tone=data.get("tone"),
            plot_point=data.get("plotPoint"),
        )

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
            validated_input = self.validate_element_data(input_data)

            # Adjust total elements if needed
            if validated_input.element_number > validated_input.total_elements:
                validated_input.total_elements = validated_input.element_number

            # Add to history
            self.element_history.append(validated_input)

            # Handle branches
            if validated_input.branch_from_element and validated_input.branch_id:
                if validated_input.branch_id not in self.branches:
                    self.branches[validated_input.branch_id] = []
                self.branches[validated_input.branch_id].append(validated_input)

            # Display the formatted element
            self.console.print(self.format_element(validated_input))

            # Return result
            return {
                "content": [
                    {
                        "type": "text",
                        "text": {
                            "elementNumber": validated_input.element_number,
                            "totalElements": validated_input.total_elements,
                            "nextElementNeeded": validated_input.next_element_needed,
                            "branches": list(self.branches.keys()),
                            "elementHistoryLength": len(self.element_history),
                        },
                    }
                ]
            }
        except Exception as e:
            error_result: ProcessResult = {
                "content": [
                    {
                        "type": "text",
                        "text": {
                            "error": str(e),
                            "status": "failed",
                        },
                    }
                ],
                "isError": True,
            }
            return error_result
