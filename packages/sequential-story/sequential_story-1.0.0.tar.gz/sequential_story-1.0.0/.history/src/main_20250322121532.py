#!/usr/bin/env python3
"""Sequential Story MCP Server - A narrative-based mnemonic tool."""

import logging
import sys

from .server import SequentialStoryServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("sequential_story")


def main() -> None:
    """Entry point for the Sequential Story MCP Server."""
    server = SequentialStoryServer()

    try:
        logger.info("Starting Sequential Story MCP Server...")
        server.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception:
        logger.exception("Unhandled exception")
        sys.exit(1)


if __name__ == "__main__":
    main()
