"""
Utilities for handling terminal input and escape sequences.

This module provides functions to help with proper terminal input handling
for Textual applications.
"""

import os
import sys
from contextlib import contextmanager
from script_magic.logger import get_logger

logger = get_logger(__name__)

def setup_terminal_for_textual():
    """
    Configure terminal settings to work better with Textual TUI.
    
    This should be called before launching a Textual app to ensure
    terminal escape sequences are properly handled.
    """
    try:
        # Set environment variable to help Textual with terminal capabilities
        if not os.environ.get("TERM"):
            os.environ["TERM"] = "xterm-256color"
            
        # On Windows, ensure VT sequences are properly processed
        if sys.platform == "win32":
            import ctypes
            kernel32 = ctypes.windll.kernel32
            
            # Enable ANSI escape sequence processing
            STD_OUTPUT_HANDLE = -11
            handle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
            
            # Enable virtual terminal processing
            ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
            ENABLE_PROCESSED_INPUT = 0x0001
            DISABLE_NEWLINE_AUTO_RETURN = 0x0008  # Added to prevent newline issues
            mode = ctypes.c_ulong()
            
            # Set modes for both input and output handles
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                kernel32.SetConsoleMode(handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING | DISABLE_NEWLINE_AUTO_RETURN)
            
            # Also adjust input mode for better key handling
            STD_INPUT_HANDLE = -10
            input_handle = kernel32.GetStdHandle(STD_INPUT_HANDLE)
            input_mode = ctypes.c_ulong()
            if kernel32.GetConsoleMode(input_handle, ctypes.byref(input_mode)):
                # Configure input mode to properly handle special keys
                # Use ENABLE_EXTENDED_FLAGS to ensure extended key handling
                ENABLE_EXTENDED_FLAGS = 0x0080
                ENABLE_QUICK_EDIT_MODE = 0x0040
                
                # Disable QuickEdit mode which can interfere with arrow key handling
                new_input_mode = (input_mode.value | ENABLE_PROCESSED_INPUT | ENABLE_EXTENDED_FLAGS) & ~ENABLE_QUICK_EDIT_MODE
                kernel32.SetConsoleMode(input_handle, new_input_mode)
                
        # Set additional environment variables to help applications properly handle keys
        os.environ["PYTHONIOENCODING"] = "utf-8"
        
        # Specific fix for arrow keys in some terminals
        if sys.platform != "win32":
            # On Unix-like systems, try to set the ESCDELAY environment variable
            # This helps with arrow key escape sequence timing
            if "ESCDELAY" not in os.environ:
                os.environ["ESCDELAY"] = "25"  # 25ms is a good balance
        
        return True
    except Exception as e:
        logger.error(f"Failed to configure terminal: {str(e)}")
        return False

@contextmanager
def terminal_setup():
    """
    Context manager to set up the terminal for a Textual app and restore afterwards.
    
    Usage:
        with terminal_setup():
            app.run()
    """
    original_term = os.environ.get("TERM", "")
    original_encoding = os.environ.get("PYTHONIOENCODING", "")
    success = setup_terminal_for_textual()
    
    try:
        yield
    finally:
        # Restore original environment variables if we changed them
        if original_term and os.environ.get("TERM") != original_term:
            os.environ["TERM"] = original_term
        if original_encoding and os.environ.get("PYTHONIOENCODING") != original_encoding:
            os.environ["PYTHONIOENCODING"] = original_encoding
