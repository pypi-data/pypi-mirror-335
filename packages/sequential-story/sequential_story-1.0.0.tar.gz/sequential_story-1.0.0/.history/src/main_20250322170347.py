"""Entry point for sequential-story MCP server.

This module provides a main function that serves as the entry point for the sequential-story
package when installed and executed via the command line.
"""

import sys

from sequential_tools import server


def main():
    """Execute the sequential-story MCP server.

    This function is used as the entry point when the package is installed
    and executed via the command line.
    """
    try:
        server.run()
    except KeyboardInterrupt:
        print("Server stopped by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
