"""
Implementation of the 'list' command for Script Magic.

This module handles listing all available scripts from the local mapping.
"""

import click
import sys
from datetime import datetime
from typing import List

from script_magic.mapping_manager import get_mapping_manager
from script_magic.rich_output import console
from rich.table import Table
from rich.panel import Panel
from rich import box
from script_magic.logger import get_logger

# Set up logger
logger = get_logger(__name__)

def format_timestamp(timestamp_str: str) -> str:
    """Format an ISO timestamp string to a more readable format."""
    try:
        if not timestamp_str:
            return "N/A"
        dt = datetime.fromisoformat(timestamp_str)
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return timestamp_str

def list_scripts(verbose: bool = False, tags: List[str] = None) -> bool:
    """
    List all scripts in the local mapping.
    
    Args:
        verbose: Whether to display detailed script information
        tags: Filter scripts by these tags (if provided)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        mapping_manager = get_mapping_manager()
        scripts = mapping_manager.list_scripts()
        
        if not scripts:
            console.print(Panel("[italic]No scripts found in your inventory.[/italic]", 
                               title="Script Magic", 
                               border_style="blue"))
            return True
            
        # Filter by tags if specified
        if tags:
            filtered_scripts = []
            for script in scripts:
                script_tags = script.get("tags", [])
                if any(tag in script_tags for tag in tags):
                    filtered_scripts.append(script)
            scripts = filtered_scripts
            
            if not scripts:
                console.print(Panel(f"[italic]No scripts found with tags: {', '.join(tags)}[/italic]", 
                                   title="Script Magic", 
                                   border_style="yellow"))
                return True
        
        # Create and populate the table
        table = Table(box=box.ROUNDED, border_style="blue", title="Available Scripts")
        
        # Define columns based on verbosity
        table.add_column("Name", style="cyan bold")
        table.add_column("Description", style="green")
        
        if verbose:
            table.add_column("Gist ID", style="dim")
            table.add_column("Created At", style="yellow")
            table.add_column("Tags", style="magenta")
        
        # Add rows to the table
        for script in sorted(scripts, key=lambda s: s["name"]):
            row = [
                script["name"],
                script.get("description", "No description available")
            ]
            
            if verbose:
                row.extend([
                    script.get("gist_id", "Unknown"),
                    format_timestamp(script.get("created_at")),
                    ", ".join(script.get("tags", [])) or "No tags"
                ])
                
            table.add_row(*row)
        
        # Display the table
        console.print("\n")
        console.print(table)
        console.print("\n")
        
        # Display summary
        tags_summary = {}
        for script in scripts:
            for tag in script.get("tags", []):
                tags_summary[tag] = tags_summary.get(tag, 0) + 1
        
        if tags_summary and verbose:
            tags_text = " ".join([f"[{color}]{tag}[/{color}] ({count})"
                                for color, (tag, count) in 
                                zip(["blue", "green", "yellow", "magenta", "cyan"] * 10, 
                                    sorted(tags_summary.items()))])
            
            console.print(Panel(tags_text, title="Tags Summary", border_style="dim"))
        
        console.print(f"[bold blue]{len(scripts)} scripts[/bold blue] in your inventory\n")
        return True
        
    except Exception as e:
        console.print(f"[bold red]Error listing scripts:[/bold red] {str(e)}")
        logger.error(f"Script listing error: {str(e)}", exc_info=True)
        return False

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Show detailed information')
@click.option('--tag', '-t', multiple=True, help='Filter scripts by tag')
def cli(verbose: bool, tag: tuple) -> None:
    """List all available scripts in your inventory."""
    success = list_scripts(verbose=verbose, tags=list(tag) if tag else None)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    cli()
