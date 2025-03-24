"""Sequential Story - Main entry point.

This module provides the main entry point for the Sequential Story package.
"""

import json
import sys

from src.server import SequentialToolsServer
from src.utils.logging import get_logger, setup_logging
from src.utils.settings import get_settings

# Set up logging
setup_logging()
logger = get_logger("sequential_tools")

# Create server instance
server = SequentialToolsServer()


def main() -> None:
    """Entry point function for the sequential-story command."""
    try:
        settings = get_settings()
        logger.info("Starting Sequential Story MCP Server...")
        logger.info("Server metadata: %s", json.dumps(settings.server_metadata, indent=2))
        logger.info("Enabled tools: %s", ", ".join(settings.enabled_tools))

        server.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception:
        logger.exception("Unhandled exception")
        sys.exit(1)


# When running as a script directly
if __name__ == "__main__":
    main()
