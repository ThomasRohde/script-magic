"""
Implementation of the 'code' command for Script Magic.

This module handles creating a script stub, saving it to the script folder,
updating the mapping JSON file, and opening an editor using SM_EDITOR
environment variable.
"""

import os
import sys
import subprocess
import platform
import click
import datetime
from pathlib import Path
from typing import Optional

from script_magic.mapping_manager import get_mapping_manager, LOCAL_SCRIPTS_DIR
from script_magic.github_integration import upload_script_to_gist, GitHubIntegrationError
from script_magic.rich_output import console, display_heading
from script_magic.logger import get_logger

# Set up logger
logger = get_logger(__name__)

# Script template with PEP 723 metadata
SCRIPT_TEMPLATE = """# /// script
# description = "{description}"
# authors = ["Script-Magic User"]
# date = "{date}"
# requires-python = ">=3.9"
# dependencies = [
#     # List required packages here
# ]
# tags = ["script-magic", "custom"]
# ///

"""

def get_vscode_path() -> Optional[str]:
    """
    Find the VS Code executable path based on the operating system.

    Returns:
        Optional[str]: Path to VS Code executable or None if not found
    """
    system = platform.system()

    if system == "Windows":
        # Check common installation paths on Windows
        possible_paths = [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Microsoft VS Code", "Code.exe"),
            os.path.join(os.environ.get("ProgramFiles", ""), "Microsoft VS Code", "Code.exe"),
            os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Microsoft VS Code", "Code.exe"),
        ]

        # Check if code is in PATH
        try:
            import shutil
            path = shutil.which("code")
            if path:
                return path
        except Exception:
            pass

        for path in possible_paths:
            if os.path.isfile(path):
                return path

    elif system == "Darwin":  # macOS
        # Common macOS installation paths
        possible_paths = [
            "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code",
            "/Applications/VSCode.app/Contents/Resources/app/bin/code",
        ]

        # Check if code is in PATH
        try:
            import shutil
            path = shutil.which("code")
            if path:
                return path
        except Exception:
            pass

        for path in possible_paths:
            if os.path.isfile(path):
                return path

    else:  # Linux
        # On Linux, try to find in PATH
        try:
            import shutil
            return shutil.which("code")
        except Exception:
            pass

    return None

def open_editor(file_path: str, editor_cmd: Optional[str] = None) -> bool:
    """
    Open a file in an editor.

    Args:
        file_path: Path to the file to open
        editor_cmd: Editor command to use (optional)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get editor command from environment variable or use default
        editor = editor_cmd or os.environ.get("SM_EDITOR")

        # If no editor specified, try to find VS Code
        if not editor:
            vscode_path = get_vscode_path()
            if (vscode_path):
                editor = f'"{vscode_path}"'
            else:
                # Fall back to system default
                if platform.system() == "Windows":
                    editor = "notepad"
                elif platform.system() == "Darwin":  # macOS
                    editor = "open -t"
                else:
                    editor = os.environ.get("EDITOR", "vim")

        # Format the command to open the file
        if "{}" in editor:
            cmd = editor.format(file_path)
        else:
            cmd = f'{editor} "{file_path}"'

        logger.debug(f"Opening editor with command: {cmd}")

        # Execute the command
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # For non-blocking behavior, we don't wait for the process to complete
        return True

    except Exception as e:
        logger.error(f"Error opening editor: {str(e)}")
        console.print(f"[bold red]Error opening editor:[/bold red] {str(e)}")
        return False

def create_script_stub(script_name: str, description: str) -> bool:
    """
    Create a script stub file and save it to the script folder.

    Args:
        script_name: Name of the script
        description: Brief description of the script

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create the script directory if it doesn't exist
        os.makedirs(LOCAL_SCRIPTS_DIR, exist_ok=True)

        # Check if script with the same name already exists
        file_path = os.path.join(LOCAL_SCRIPTS_DIR, f"{script_name}.py")
        if os.path.exists(file_path):
            logger.info(f"Script '{script_name}' already exists at: {file_path}")
            return file_path

        # Generate script content with template
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        script_content = SCRIPT_TEMPLATE.format(
            description=description,
            date=today
        )

        # Add Python script boilerplate
        script_content += f"""
# {script_name}.py - {description}
# Created using Script Magic's 'code' command

import argparse


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="{description}")

    # Add arguments here
    # parser.add_argument("--example", help="An example argument")

    args = parser.parse_args()

    # Your code here
    print("Hello from {script_name}!")


if __name__ == "__main__":
    main()
"""

        # Save the script to file
        file_path = os.path.join(LOCAL_SCRIPTS_DIR, f"{script_name}.py")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(script_content)

        logger.info(f"Created script stub at: {file_path}")
        return file_path

    except Exception as e:
        logger.error(f"Error creating script stub: {str(e)}")
        console.print(f"[bold red]Error creating script stub:[/bold red] {str(e)}")
        return False

def update_mapping(script_name: str, description: str, publish_to_gist: bool) -> bool:
    """
    Update the mapping JSON file with the new script.

    Args:
        script_name: Name of the script
        description: Brief description of the script
        publish_to_gist: Whether to publish the script to a GitHub Gist

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        mapping_manager = get_mapping_manager()
        file_path = os.path.join(LOCAL_SCRIPTS_DIR, f"{script_name}.py")

        if not os.path.exists(file_path):
            logger.error(f"Script file not found at: {file_path}")
            return False

        # Read the script content
        with open(file_path, "r", encoding="utf-8") as f:
            script_content = f.read()

        # Upload to GitHub Gist if requested
        gist_id = None
        if publish_to_gist:
            try:
                console.print("\n[bold blue]Uploading to GitHub Gist...[/bold blue]")
                gist_id = upload_script_to_gist(
                    script_name=script_name,
                    script_content=script_content,
                    description=description[:50] + ("..." if len(description) > 50 else "")
                )
                console.print(f"[green]✓ Script uploaded to GitHub Gist[/green]")
            except GitHubIntegrationError as e:
                logger.error(f"GitHub integration error: {str(e)}")
                console.print(f"[yellow]Warning: Could not upload to GitHub Gist: {str(e)}[/yellow]")

        # Update local mapping
        console.print("[bold blue]Updating local mapping...[/bold blue]")

        # Get current timestamp
        timestamp = datetime.datetime.now().isoformat()

        # Add metadata
        metadata = {
            "description": description,
            "created_at": timestamp,
            "modified_at": timestamp,
            "tags": ["custom"]
        }

        if gist_id:
            mapping_manager.add_script(
                script_name=script_name,
                gist_id=gist_id,
                metadata=metadata,
                sync=publish_to_gist
            )
        else:
            # Add to mapping without Gist ID
            mapping_manager.update_script(
                script_name=script_name,
                metadata=metadata
            )

        console.print("[green]✓ Script added to local inventory[/green]")
        return True

    except Exception as e:
        logger.error(f"Error updating mapping: {str(e)}")
        console.print(f"[bold red]Error updating mapping:[/bold red] {str(e)}")
        return False

def code_command(script_name: str, description: str, publish: bool, editor: Optional[str] = None) -> bool:
    """
    Create a script stub, save it to the script folder, update the mapping,
    and open it in an editor.

    Args:
        script_name: Name of the script
        description: Brief description of the script
        publish: Whether to publish the script to a GitHub Gist
        editor: Editor command to use (optional)

    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Creating script stub '{script_name}' with description: {description}")

    try:
        # Display header
        display_heading(f"Creating script: {script_name}", style="bold blue")
        console.print(f"[italic]Description:[/italic] {description}\n")

        # First check if script with the same name already exists
        file_path = os.path.join(LOCAL_SCRIPTS_DIR, f"{script_name}.py")
        if os.path.exists(file_path):
            console.print(f"[yellow]Script named '{script_name}' already exists![/yellow]")
            console.print("[blue]Opening existing script in editor...[/blue]")

            # Open the existing script in editor
            editor_success = open_editor(file_path, editor)
            if not editor_success:
                console.print("[yellow]Warning: Could not open editor. You can edit the file manually.[/yellow]")
                console.print(f"[dim]File location: {file_path}[/dim]")

            return True

        # Step 1: Create script stub
        console.print("[bold blue]Creating script stub...[/bold blue]")
        file_path = create_script_stub(script_name, description)
        if not file_path:
            return False
        console.print(f"[green]✓ Script stub created at {file_path}[/green]")

        # Step 2: Update mapping JSON
        success = update_mapping(script_name, description, publish)
        if not success:
            console.print("[yellow]Warning: Script was created but mapping was not updated.[/yellow]")

        # Step 3: Open in editor
        console.print("[bold blue]Opening script in editor...[/bold blue]")
        editor_success = open_editor(file_path, editor)
        if not editor_success:
            console.print("[yellow]Warning: Could not open editor. You can edit the file manually.[/yellow]")
            console.print(f"[dim]File location: {file_path}[/dim]")

        return True

    except Exception as e:
        console.print(f"[bold red]Error creating script:[/bold red] {str(e)}")
        logger.error(f"Script creation error: {str(e)}", exc_info=True)
        return False

@click.command()
@click.argument('script_name')
@click.argument('description', required=False, default="")
@click.option('--publish/--no-publish', '-p/', default=True,
              help='Whether to publish the script to GitHub Gist (default: True)')
@click.option('--editor', '-e', help='Editor command to use (overrides SM_EDITOR environment variable)')
def cli(script_name: str, description: str, publish: bool, editor: Optional[str]) -> None:
    """
    Create a script stub and open it in an editor.

    SCRIPT_NAME: Name of the script to create

    DESCRIPTION: Optional brief description of the script
    """
    # If no description provided, use the script name
    if not description:
        description = f"Script created with the 'code' command: {script_name}"

    # Check GitHub environment variable if publishing
    if publish and not os.getenv("MY_GITHUB_PAT"):
        console.print("[yellow]Warning:[/yellow] MY_GITHUB_PAT environment variable is not set. "
                     "Script will be created locally only.")
        publish = False

    # Run the code command
    success = code_command(script_name, description, publish, editor)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    cli()
