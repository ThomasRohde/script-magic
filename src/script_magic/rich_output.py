"""
Rich-based output utilities for displaying formatted code and text.

This module provides functions for displaying syntax-highlighted code and other
formatted text using the Rich package.
"""
from rich.console import Console
from rich.syntax import Syntax
from typing import Optional

# Create a global console object for reuse
console = Console()

def display_code(
    code: str, 
    language: str = "python", 
    line_numbers: bool = True,
    title: Optional[str] = None,
    theme: str = "monokai"
) -> None:
    """
    Display syntax-highlighted code using Rich.
    
    Args:
        code: The code to display
        language: Programming language for syntax highlighting
        line_numbers: Whether to show line numbers
        title: Optional title for the code block
        theme: Syntax highlighting theme
    """
    syntax = Syntax(
        code, 
        language, 
        line_numbers=line_numbers,
        theme=theme,
        word_wrap=True
    )
    
    console.print()
    if title:
        console.rule(title)
    console.print(syntax)
    console.print()

def display_heading(text: str, style: str = "bold cyan") -> None:
    """
    Display a styled heading.
    
    Args:
        text: The heading text
        style: Rich style string for the heading
    """
    console.print(f"\n{text}", style=style)

def create_init_file():
    """Create an __init__.py file to make the utils directory a proper package."""
    pass  # Implementation would create the __init__.py file if needed
