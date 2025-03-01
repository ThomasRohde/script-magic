"""
Implementation of the 'list' command for Script Magic.

This module handles listing all scripts in the inventory and can trigger mapping sync.
"""

import click
import sys
import datetime
from typing import List, Dict, Any, Optional
from rich.table import Table
from rich.box import ROUNDED
from rich.panel import Panel

from script_magic.mapping_manager import get_mapping_manager
from script_magic.rich_output import console, display_heading
from script_magic.logger import get_logger
from script_magic.github_integration import GitHubIntegrationError

# Set up logger
logger = get_logger(__name__)

def format_scripts_table(scripts: List[Dict[str, Any]], verbose: bool = False) -> Table:
    """
    Format scripts as a Rich table.
    
    Args:
        scripts: List of script dictionaries
        verbose: Whether to include detailed information
        
    Returns:
        Table: Formatted Rich table
    """
    if not scripts:
        return Panel("No scripts found in inventory.", border_style="yellow")
    
    # Create a Rich table with rounded borders
    table = Table(box=ROUNDED, highlight=True, expand=True)
    
    # Determine what columns to show based on verbosity
    if verbose:
        table.add_column("Name", style="cyan bold", no_wrap=True)
        table.add_column("Description", style="green")
        table.add_column("Gist ID", style="blue dim")
        table.add_column("Created", style="magenta")
        
        for script in scripts:
            # Parse ISO format date if available
            created_at = script.get('created_at')
            if created_at:
                try:
                    date_obj = datetime.datetime.fromisoformat(created_at)
                    created_at = date_obj.strftime('%Y-%m-%d %H:%M')
                except (ValueError, TypeError):
                    pass  # Keep original string if parsing fails
            
            description = script.get('description', 'No description')
            if len(description) > 50:
                description = description[:50] + "..."
                
            table.add_row(
                script['name'],
                description,
                script.get('gist_id', 'Unknown'),
                created_at or 'Unknown'
            )
    else:
        # Simple list with just name and short description
        table.add_column("Name", style="cyan bold", no_wrap=True)
        table.add_column("Description", style="green")
        
        for script in scripts:
            description = script.get('description', 'No description')
            if len(description) > 70:
                description = description[:70] + "..."
                
            table.add_row(script['name'], description)
    
    return table

def list_scripts(verbose: bool = False, push: bool = False, pull: bool = False) -> bool:
    """
    List all scripts in the inventory.
    
    Args:
        verbose: Whether to show detailed information
        push: Whether to push local mapping to GitHub before listing
        pull: Whether to pull mapping from GitHub before listing
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        mapping_manager = get_mapping_manager()
        
        # Push to GitHub if requested
        if push:
            console.print(Panel("Pushing mapping to GitHub...", border_style="blue"))
            if mapping_manager.sync_mapping():
                console.print(Panel("✓ Mapping pushed successfully", border_style="green"))
            else:
                console.print(Panel("⚠ Could not push mapping to GitHub", border_style="yellow"))
        
        # Pull from GitHub if requested
        if pull:
            console.print(Panel("Pulling mapping from GitHub...", border_style="blue"))
            if mapping_manager.pull_mapping():
                console.print(Panel("✓ Mapping pulled successfully", border_style="green"))
            else:
                console.print(Panel("⚠ Could not pull mapping from GitHub", border_style="yellow"))
        
        # Get all scripts
        scripts = mapping_manager.list_scripts()
        
        # Display the scripts
        display_heading("Script Inventory", style="bold blue on white")
        
        if not scripts:
            console.print(Panel("[yellow]No scripts found in your inventory.[/yellow]\n\nUse [bold cyan]sm create <script_name> <prompt>[/bold cyan] to create a new script.", 
                              title="Empty Inventory", border_style="yellow", expand=False))
            return True
            
        # Sort scripts by name
        scripts.sort(key=lambda x: x['name'])
        
        # Display the table
        console.print(format_scripts_table(scripts, verbose))
        
        # Show count and hint with emoji and styling
        script_count = len(scripts)
        count_message = f"📚 Found {script_count} script{'s' if script_count != 1 else ''} in your inventory"
        
        if script_count > 10:
            count_style = "bold green"
        elif script_count > 0:
            count_style = "bold blue"
        else:
            count_style = "bold yellow"
            
        console.print(f"\n[{count_style}]{count_message}[/{count_style}]")
        
        if not verbose:
            console.print("[dim]💡 Tip: Run with [bold]--verbose[/bold] for more details[/dim]")
        
        return True
        
    except GitHubIntegrationError as e:
        console.print(Panel(f"GitHub integration error: {str(e)}", 
                           title="⚠ Warning", border_style="yellow", expand=False))
        logger.warning(f"GitHub integration error during list: {str(e)}")
        
        try:
            # Try to list scripts from local mapping only
            mapping_manager = get_mapping_manager()
            scripts = mapping_manager.list_scripts()
            
            # Sort scripts by name
            scripts.sort(key=lambda x: x['name'])
            
            display_heading("Script Inventory (Local Only)", style="yellow on black")
            console.print(format_scripts_table(scripts, verbose))
            
            script_count = len(scripts)
            console.print(f"\n[yellow]📂 Found {script_count} script{'s' if script_count != 1 else ''} in local inventory[/yellow]")
            console.print("[dim]Note: Using local data only due to GitHub integration error[/dim]")
            return True
        except Exception as inner_e:
            console.print(Panel(f"Error: {str(inner_e)}", 
                              title="❌ Error", border_style="red", expand=False))
            logger.error(f"Error listing scripts: {str(inner_e)}")
            return False
            
    except Exception as e:
        console.print(Panel(f"Error listing scripts: {str(e)}", 
                          title="❌ Error", border_style="red", expand=False))
        logger.error(f"Error listing scripts: {str(e)}", exc_info=True)
        return False

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Show detailed information about scripts')
@click.option('--push', is_flag=True, help='Push local mapping to GitHub before listing scripts')
@click.option('--pull', is_flag=True, help='Pull mapping from GitHub before listing scripts')
def cli(verbose: bool, push: bool, pull: bool) -> None:
    """
    List all scripts in your inventory.
    
    Shows a table of all available scripts with their descriptions.
    Use --verbose to see more details like Gist IDs and creation dates.
    Use --push to sync local mapping to GitHub before listing.
    Use --pull to fetch the latest mapping from GitHub before listing.
    """
    success = list_scripts(verbose, push, pull)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    cli()
