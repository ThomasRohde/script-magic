"""
Implementation of the 'list' command for Script Magic.

This module handles listing all scripts in the inventory and can trigger mapping sync.
"""

import click
import sys
import datetime
from typing import List, Dict, Any, Optional
from tabulate import tabulate

from script_magic.mapping_manager import get_mapping_manager
from script_magic.rich_output import console, display_heading
from script_magic.logger import get_logger
from script_magic.github_integration import GitHubIntegrationError

# Set up logger
logger = get_logger(__name__)

def format_scripts_table(scripts: List[Dict[str, Any]], verbose: bool = False) -> str:
    """
    Format scripts as a text table.
    
    Args:
        scripts: List of script dictionaries
        verbose: Whether to include detailed information
        
    Returns:
        str: Formatted table
    """
    if not scripts:
        return "No scripts found in inventory."
    
    # Determine what columns to show based on verbosity
    if verbose:
        headers = ["Name", "Description", "Gist ID", "Created"]
        table_data = []
        
        for script in scripts:
            # Parse ISO format date if available
            created_at = script.get('created_at')
            if created_at:
                try:
                    date_obj = datetime.datetime.fromisoformat(created_at)
                    created_at = date_obj.strftime('%Y-%m-%d %H:%M')
                except (ValueError, TypeError):
                    pass  # Keep original string if parsing fails
            
            table_data.append([
                script['name'],
                script.get('description', 'No description')[:50] + ('...' if len(script.get('description', '')) > 50 else ''),
                script.get('gist_id', 'Unknown'),
                created_at or 'Unknown'
            ])
    else:
        # Simple list with just name and short description
        headers = ["Name", "Description"]
        table_data = [
            [
                script['name'],
                script.get('description', 'No description')[:70] + ('...' if len(script.get('description', '')) > 70 else '')
            ]
            for script in scripts
        ]
    
    # Sort by name
    table_data.sort(key=lambda x: x[0])
    
    # Return formatted table
    return tabulate(table_data, headers=headers, tablefmt="grid")

def list_scripts(verbose: bool = False, sync: bool = False) -> bool:
    """
    List all scripts in the inventory.
    
    Args:
        verbose: Whether to show detailed information
        sync: Whether to sync with GitHub before listing
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        mapping_manager = get_mapping_manager()
        
        # Sync with GitHub first if requested
        if sync:
            console.print("[bold blue]Syncing mapping with GitHub...[/bold blue]")
            if mapping_manager.sync_mapping():
                console.print("[green]✓ Mapping synced successfully[/green]\n")
            else:
                console.print("[yellow]Warning: Could not sync mapping with GitHub[/yellow]\n")
        
        # Get all scripts
        scripts = mapping_manager.list_scripts()
        
        # Display the scripts
        display_heading("Script Inventory", style="bold blue")
        
        if not scripts:
            console.print("[yellow]No scripts found in your inventory.[/yellow]")
            console.print("\nUse 'sm create <script_name> <prompt>' to create a new script.")
            return True
            
        console.print(format_scripts_table(scripts, verbose))
        
        # Show count and hint
        console.print(f"\nFound {len(scripts)} script(s) in inventory.")
        console.print("[dim]Run with --verbose for more details[/dim]")
        
        return True
        
    except GitHubIntegrationError as e:
        console.print(f"[bold yellow]GitHub integration error:[/bold yellow] {str(e)}")
        logger.warning(f"GitHub integration error during list: {str(e)}")
        
        try:
            # Try to list scripts from local mapping only
            mapping_manager = get_mapping_manager()
            scripts = mapping_manager.list_scripts()
            
            display_heading("Script Inventory (Local Only)", style="yellow")
            console.print(format_scripts_table(scripts, verbose))
            console.print(f"\nFound {len(scripts)} script(s) in local inventory.")
            console.print("[dim]Note: Using local data only due to GitHub integration error[/dim]")
            return True
        except Exception as inner_e:
            console.print(f"[bold red]Error:[/bold red] {str(inner_e)}")
            logger.error(f"Error listing scripts: {str(inner_e)}")
            return False
            
    except Exception as e:
        console.print(f"[bold red]Error listing scripts:[/bold red] {str(e)}")
        logger.error(f"Error listing scripts: {str(e)}", exc_info=True)
        return False

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Show detailed information about scripts')
@click.option('--sync', '-s', is_flag=True, help='Sync with GitHub before listing scripts')
def cli(verbose: bool, sync: bool) -> None:
    """
    List all scripts in your inventory.
    
    Shows a table of all available scripts with their descriptions.
    Use --verbose to see more details like Gist IDs and creation dates.
    """
    success = list_scripts(verbose, sync)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    cli()
