"""CodeDoc MCP Server.

This module provides a FastMCP server for code analysis and enhancement.
It supports analyzing code, providing suggestions, and enhancing code quality.
"""

# Import built-in modules
import sys
from pathlib import Path

# Import third-party modules
from loguru import logger

# Import local modules
import __version__
from codedoc_mcp.app import APP_NAME
from codedoc_mcp.app import mcp
from codedoc_mcp.log_config import setup_logging

# Re-export tools for easier imports


def main() -> None:
    """Start the MCP server."""
    # Setup logging
    setup_logging()

    logger.info(f"Starting {APP_NAME} v{__version__}")

    # Run the MCP server
    mcp.run()


if __name__ == "__main__":
    main()
