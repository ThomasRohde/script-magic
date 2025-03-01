"""
Implementation for the 'run' command to execute scripts stored in GitHub Gists.
"""
import os
import sys
import click
import subprocess
from typing import List, Tuple

from script_magic.mapping_manager import get_mapping_manager
from script_magic.logger import get_logger
from script_magic.github_integration import download_script_from_gist, GitHubIntegrationError

# Set up logger for this module
logger = get_logger(__name__)

@click.command()
@click.argument('script_name')
@click.argument('params', nargs=-1)
@click.option('--refresh', '-r', is_flag=True, help='Force refresh the script from GitHub')
@click.option('--dry-run', is_flag=True, help='Download the script but don\'t execute it')
@click.option('--verbose', '-v', is_flag=True, help='Display more detailed output')
def cli(script_name: str, params: List[str], refresh: bool, dry_run: bool, verbose: bool):
    """
    Run a Python script stored in a GitHub Gist.
    
    SCRIPT_NAME is the name of the script to run.
    PARAMS are optional parameters to pass to the script (e.g., prefix=gist).
    """
    try:
        # Set up more verbose logging if requested
        if verbose:
            from script_magic.logger import set_log_level
            import logging
            set_log_level(logging.DEBUG)
            logger.debug("Verbose mode enabled")
        
        logger.info(f"Running script '{script_name}'")
        if params:
            logger.info(f"With parameters: {params}")
            
        # Step 1: Look up the script in the mapping file
        script_path, gist_id = lookup_script(script_name, refresh)
        
        if dry_run:
            click.echo(f"Dry run: script '{script_name}' (Gist ID: {gist_id}) downloaded to {script_path}")
            return
            
        # Step 2: Execute the script with uv
        execute_script_with_uv(script_path, params)
        
    except GitHubIntegrationError as e:
        logger.error(f"GitHub integration error: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error running script '{script_name}': {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

def lookup_script(script_name: str, refresh: bool = False) -> Tuple[str, str]:
    """
    Look up a script in the mapping file and download it from GitHub if necessary.
    
    Args:
        script_name: Name of the script to look up
        refresh: Whether to force refresh from GitHub
        
    Returns:
        Tuple[str, str]: Path to the downloaded script and its Gist ID
        
    Raises:
        click.ClickException: If the script is not found or cannot be downloaded
    """
    # Get the mapping manager to look up the script
    mapping_manager = get_mapping_manager()
    script_info = mapping_manager.lookup_script(script_name)
    
    if not script_info:
        error_msg = f"Script '{script_name}' not found in the mapping file"
        logger.error(error_msg)
        raise click.ClickException(error_msg)
    
    gist_id = script_info.get("gist_id")
    if not gist_id:
        error_msg = f"No Gist ID found for script '{script_name}'"
        logger.error(error_msg)
        raise click.ClickException(error_msg)
    
    # Create scripts directory if it doesn't exist
    scripts_dir = os.path.expanduser("~/.sm/scripts")
    os.makedirs(scripts_dir, exist_ok=True)
    
    # Path where we'll save the script
    script_path = os.path.join(scripts_dir, f"{script_name}.py")
    
    # Check if we need to download the script (if it doesn't exist or refresh is True)
    if refresh or not os.path.exists(script_path):
        logger.info(f"Downloading script '{script_name}' from Gist {gist_id}")
        try:
            # Download the script from GitHub
            script_content, _ = download_script_from_gist(gist_id)
            
            # Save the script to a file with UTF-8 encoding
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
                
            logger.info(f"Script downloaded to {script_path}")
        except GitHubIntegrationError as e:
            logger.error(f"Failed to download script '{script_name}': {str(e)}")
            raise click.ClickException(f"Failed to download script: {str(e)}")
    else:
        logger.info(f"Using cached script at {script_path}")
    
    return script_path, gist_id

def execute_script_with_uv(script_path: str, params: List[str]) -> None:
    """
    Execute a Python script using the uv package manager.
    
    Args:
        script_path: Path to the script file
        params: List of parameters to pass to the script
        
    Raises:
        Exception: If the script execution fails
    """
    # Build the command to execute the script with uv run
    cmd = ["uv", "run", script_path]
    
    # Add any parameters
    cmd.extend(params)
    
    logger.debug(f"Executing command: {' '.join(cmd)}")
    
    try:
        # Execute the script and capture the output with UTF-8 encoding
        process = subprocess.run(
            cmd,
            text=True,
            capture_output=True,
            encoding='utf-8'
        )
        
        # Display the output
        if process.stdout:
            click.echo(process.stdout)
            
        # Check for errors
        if process.returncode != 0:
            if process.stderr:
                logger.error(f"Script execution failed with error: {process.stderr}")
                click.echo(f"Error: {process.stderr}", err=True)
            raise Exception(f"Script exited with non-zero status code: {process.returncode}")
            
        logger.info(f"Script '{os.path.basename(script_path)}' executed successfully")
        
    except FileNotFoundError:
        error_msg = "The 'uv' package manager could not be found. Please ensure it's installed (https://astral.sh/uv)."
        logger.error(error_msg)
        raise click.ClickException(error_msg)
    except subprocess.SubprocessError as e:
        logger.error(f"Error executing script: {str(e)}")
        raise click.ClickException(f"Error executing script: {str(e)}")
