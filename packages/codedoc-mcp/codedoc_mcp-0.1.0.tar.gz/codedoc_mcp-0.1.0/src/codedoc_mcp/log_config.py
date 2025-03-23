"""Logging configuration for CodeDoc MCP Server."""

# Import built-in modules
import os
import sys
from pathlib import Path

# Import third-party modules
from loguru import logger
from platformdirs import user_log_dir

# Constants
APP_NAME = "codedoc_mcp_server"


def setup_logging() -> None:
    """Set up logging configuration.
    
    Configures loguru logger with appropriate format and log file location.
    """
    # Create log directory if it doesn't exist
    log_dir = Path(user_log_dir(APP_NAME))
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Log file path
    log_file = log_dir / "codedoc_mcp.log"
    
    # Configure logger
    logger.remove()  # Remove default handler
    
    # Add console handler
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )
    
    # Add file handler
    logger.add(
        log_file,
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="1 week",
    )
    
    logger.info(f"Log file: {log_file}")
