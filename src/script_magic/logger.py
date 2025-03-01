"""
Logging configuration and utilities.

This module provides a standardized logging configuration for the script-magic application.
"""
import os
import logging
from logging.handlers import RotatingFileHandler
import sys
from typing import Optional

# Default logging directory and file
DEFAULT_LOG_DIR = os.path.expanduser("~/.sm/logs")
DEFAULT_LOG_FILE = os.path.join(DEFAULT_LOG_DIR, "script-magic.log")

# Ensure log directory exists
os.makedirs(DEFAULT_LOG_DIR, exist_ok=True)

# Configure logging format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Set up root logger
root_logger = logging.getLogger("script-magic")
root_logger.setLevel(logging.INFO)

# Create console handler
console_handler = logging.StreamHandler(stream=sys.stdout)
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
console_handler.setFormatter(console_formatter)

# Create file handler
try:
    file_handler = RotatingFileHandler(
        DEFAULT_LOG_FILE,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    
    # Add handlers to root logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
except (IOError, PermissionError) as e:
    # Fall back to console only if file logging fails
    print(f"Warning: Could not set up file logging: {e}")
    print(f"Logging to console only.")
    root_logger.addHandler(console_handler)

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (usually __name__ of the calling module)
        
    Returns:
        A configured logger instance
    """
    if name is None:
        return root_logger
    
    # Return a child logger with appropriate name
    logger = root_logger.getChild(name)
    return logger

def set_log_level(level: int) -> None:
    """
    Set the log level for all handlers.
    
    Args:
        level: Logging level (e.g. logging.DEBUG, logging.INFO)
    """
    root_logger.setLevel(level)
    for handler in root_logger.handlers:
        handler.setLevel(level)
    
    root_logger.debug(f"Log level set to {logging.getLevelName(level)}")

def create_init_file():
    """Create an __init__.py file in the logs directory to make it a proper package."""
    init_path = os.path.join(os.path.dirname(__file__), "__init__.py")
    if not os.path.exists(init_path):
        with open(init_path, 'w') as f:
            f.write('"""Logger utilities for script-magic."""\n')
