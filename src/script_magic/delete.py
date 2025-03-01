"""
Implementation of the 'delete' command for Script Magic.

This module handles the deletion of scripts from both the local mapping
and the GitHub Gists where they are stored.
"""

import click
import sys
from github import GithubException

from script_magic.mapping_manager import get_mapping_manager
from script_magic.github_integration import get_github_client, GitHubIntegrationError
from script_magic.rich_output import console, display_heading
from script_magic.logger import get_logger

# Set up logger
logger = get_logger(__name__)

def delete_script(script_name: str, force: bool = False) -> bool:
    """
    Delete a script from both the local mapping and GitHub Gist.
    
    Args:
        script_name: Name of the script to delete
        force: Whether to skip confirmation
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Attempting to delete script: {script_name}")
    
    try:
        # Get the mapping manager and find the script
        mapping_manager = get_mapping_manager()
        script_info = mapping_manager.get_script_info(script_name)
        
        if not script_info:
            console.print(f"[bold red]Error:[/bold red] Script '{script_name}' not found in your inventory")
            return False
            
        # Display script details and confirm deletion
        display_heading(f"Delete Script: {script_name}", style="bold red")
        
        console.print(f"[bold]Description:[/bold] {script_info.get('description', 'No description')}")
        console.print(f"[bold]Gist ID:[/bold] {script_info.get('gist_id', 'Unknown')}")
        if script_info.get('tags'):
            console.print(f"[bold]Tags:[/bold] {', '.join(script_info.get('tags', []))}")
        console.print()
        
        # Confirm deletion unless force is specified
        if not force and not click.confirm("Are you sure you want to delete this script? This action cannot be undone", default=False):
            console.print("[yellow]Deletion canceled.[/yellow]")
            return False
        
        # Delete from GitHub if we have a Gist ID
        gist_id = script_info.get('gist_id')
        if gist_id:
            try:
                console.print("[blue]Deleting from GitHub Gist...[/blue]")
                github_client = get_github_client()
                
                try:
                    gist = github_client.get_gist(gist_id)
                    gist.delete()
                    console.print("[green]✓ Deleted from GitHub successfully[/green]")
                except GithubException as ge:
                    # If the gist is not found (404), we can still continue with local deletion
                    if ge.status == 404:
                        console.print(f"[yellow]Note:[/yellow] The Gist with ID {gist_id} no longer exists on GitHub")
                        logger.warning(f"Gist {gist_id} not found on GitHub (already deleted or invalid ID)")
                    else:
                        # For other GitHub exceptions, raise to be caught by the outer exception handler
                        raise
                        
            except GitHubIntegrationError as e:
                console.print(f"[bold yellow]Warning:[/bold yellow] Could not delete GitHub Gist: {str(e)}")
                logger.warning(f"Failed to delete Gist {gist_id}: {str(e)}")
                
                # Confirm whether to continue with local deletion
                if not force and not click.confirm("Continue with local deletion?", default=True):
                    console.print("[yellow]Deletion canceled.[/yellow]")
                    return False
        
        # Delete from local mapping
        console.print("[blue]Removing from local inventory...[/blue]")
        mapping_manager.remove_script(script_name)
        console.print("[green]✓ Removed from local inventory successfully[/green]")
        
        console.print(f"[bold green]Script '{script_name}' has been deleted.[/bold green]")
        return True
        
    except Exception as e:
        console.print(f"[bold red]Error deleting script:[/bold red] {str(e)}")
        logger.error(f"Script deletion error: {str(e)}", exc_info=True)
        return False

@click.command()
@click.argument('script_name')
@click.option('--force', '-f', is_flag=True, help='Skip confirmation prompts')
def cli(script_name: str, force: bool) -> None:
    """
    Delete a script from both local inventory and GitHub Gist.
    
    SCRIPT_NAME: Name of the script to delete
    """
    success = delete_script(script_name, force)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    cli()
