#!/usr/bin/env python3
"""Sequential Story MCP Server - A narrative-based mnemonic tool."""

import logging
import sys

from .server import SequentialStoryServer

# Create a dedicated logger for the application
logger = logging.getLogger("sequential_story")


def setup_logging() -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )


def run_server() -> None:
    """Run the Sequential Story MCP Server."""
    server = SequentialStoryServer()
    try:
        logger.info("Starting Sequential Story MCP Server...")
        server.run()
    except Exception:
        logger.exception("Fatal error running server")
        sys.exit(1)


def main() -> None:
    """Entry point for the Sequential Story MCP Server."""
    setup_logging()

    try:
        run_server()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception:
        logger.exception("Unhandled exception")
        sys.exit(1)


if __name__ == "__main__":
    main()
