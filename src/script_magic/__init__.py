import click
import logging
import sys
import pip_system_certs.wrapt_requests

# Import command implementations
from script_magic.create import cli as create_command
from script_magic.run import cli as run_command
from script_magic.list import cli as list_command
from script_magic.delete import cli as delete_command
from script_magic.edit import cli as edit_command
from script_magic.mapping_setup import setup_mapping
from script_magic.logger import get_logger, set_log_level
from script_magic.mapping_manager import get_mapping_manager
from script_magic.rich_output import console

logger = get_logger(__name__)

@click.group()
@click.option('--debug', is_flag=True, help='Enable debug logging')
def sm(debug):
    """Script Magic - A tool for creating and running Python scripts with GitHub Gists."""
    try:
        # Set debug logging if requested
        if debug:
            set_log_level(logging.DEBUG)
            logger.debug("Debug logging enabled")
        
        # Initialize mapping on startup
        mapping_manager, github_success = setup_mapping()
        if github_success:
            logger.debug("GitHub integration initialized successfully")
    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        # Continue anyway to allow local operation

@click.command()
def push():
    """Sync your script inventory and all scripts with GitHub."""
    try:
        console.print("[bold blue]Syncing scripts and mapping with GitHub...[/bold blue]")
        mapping_manager = get_mapping_manager()
        
        # Push all scripts first
        results = mapping_manager.push_all_scripts()
        
        # Report results
        if results["success"]:
            console.print(f"[bold green]✓ Successfully pushed {len(results['success'])} scripts to GitHub:[/bold green]")
            for script in results["success"]:
                console.print(f"  - {script}")
                
        if results["failed"]:
            console.print(f"[bold red]⚠ Failed to push {len(results['failed'])} scripts:[/bold red]")
            for script in results["failed"]:
                console.print(f"  - {script}")
                
        console.print("[bold green]✓ Mapping synced successfully![/bold green]")
        return len(results["failed"]) == 0
    except Exception as e:
        console.print(f"[bold red]Error syncing scripts and mapping:[/bold red] {str(e)}")
        logger.error(f"Error during manual sync: {str(e)}", exc_info=True)
        sys.exit(1)

@click.command()
def pull():
    """Pull the latest scripts and mapping from GitHub."""
    try:
        console.print("[bold blue]Pulling scripts and mapping from GitHub...[/bold blue]")
        mapping_manager = get_mapping_manager()
        
        # Pull all scripts
        results = mapping_manager.pull_all_scripts()
        
        # Report results
        if results["success"]:
            console.print(f"[bold green]✓ Successfully pulled {len(results['success'])} scripts from GitHub:[/bold green]")
            for script in results["success"]:
                console.print(f"  - {script}")
                
        if results["failed"]:
            console.print(f"[bold yellow]⚠ Failed to pull {len(results['failed'])} scripts:[/bold yellow]")
            for script in results["failed"]:
                console.print(f"  - {script}")
                
        console.print("[bold green]✓ Mapping pulled successfully![/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error pulling scripts and mapping:[/bold red] {str(e)}")
        logger.error(f"Error during pull: {str(e)}", exc_info=True)
        sys.exit(1)

# Register commands
sm.add_command(create_command, name='create')
sm.add_command(run_command, name='run')
sm.add_command(list_command, name='list')
sm.add_command(delete_command, name='delete')
sm.add_command(edit_command, name='edit')
sm.add_command(push, name='push')
sm.add_command(pull, name='pull')

if __name__ == '__main__':
    sm()
