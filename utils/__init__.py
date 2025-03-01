"""
Utility modules for script-magic.

This package contains various utility functions and classes used throughout
the script-magic application.
"""

# Make key utilities available at the package level
from .rich_output import display_code, display_heading, console
from .logger import get_logger, set_log_level
from .mapping_manager import get_mapping_manager

__all__ = [
    'display_code', 
    'display_heading',
    'console',
    'get_logger',
    'set_log_level',
    'get_mapping_manager'
]
