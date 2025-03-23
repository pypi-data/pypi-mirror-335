from dataclasses import dataclass
from typing import Any

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


class SequentialStoryProcessor:
    """Processor for sequential storytelling with mnemonic elements."""

    def __init__(self):
        """Initialize the story processor with empty history and branches."""
        self.element_history: list[StoryElementData] = []
        self.branches: dict[str, list[StoryElementData]] = {}
        self.console = Console(stderr=True)

    def validate_element_data(self, data: Any) -> StoryElementData:
        """Validate input data and convert to StoryElementData.

        Args:
            data: Input data to validate

        Returns:
            StoryElementData: Validated data as StoryElementData object

        Raises:
            ValueError: If data validation fails

        """
        if not isinstance(data, dict):
            raise ValueError("Input must be a dictionary")

        # Check required fields
        required_fields = ["element", "elementNumber", "totalElements", "nextElementNeeded"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Validate types of required fields
        if not isinstance(data["element"], str):
            raise ValueError("element must be a string")
        if not isinstance(data["elementNumber"], int):
            raise ValueError("elementNumber must be an integer")
        if not isinstance(data["totalElements"], int):
            raise ValueError("totalElements must be an integer")
        if not isinstance(data["nextElementNeeded"], bool):
            raise ValueError("nextElementNeeded must be a boolean")

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
            Panel: A rich Panel object for display

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
        return Panel(Text(element_data.element), title=header, border_style=style)

    def process_element(self, input_data: Any) -> dict[str, Any]:
        """Process a new story element.

        Args:
            input_data: Input data for the story element

        Returns:
            Dict: Result of processing with content and optional error flag

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
            return {"content": [{"type": "text", "text": {"error": str(e), "status": "failed"}}], "isError": True}
