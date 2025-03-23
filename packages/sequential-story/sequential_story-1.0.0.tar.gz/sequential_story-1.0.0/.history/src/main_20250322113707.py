#!/usr/bin/env python3
"""Sequential Story MCP Server - A narrative-based mnemonic tool."""

import asyncio
import logging
import sys
from typing import NoReturn

from .server import SequentialStoryServer


def setup_logging() -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )


async def run_server() -> NoReturn:
    """Run the Sequential Story MCP Server.

    This function doesn't return under normal operation.
    """
    server = SequentialStoryServer()
    try:
        logging.info("Starting Sequential Story MCP Server...")
        await server.run()
    except Exception as e:
        logging.exception(f"Fatal error running server: {e}")
        sys.exit(1)


def main() -> NoReturn:
    """Entry point for the Sequential Story MCP Server."""
    setup_logging()

    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logging.exception(f"Unhandled exception: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
