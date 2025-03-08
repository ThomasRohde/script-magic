"""
Implementation of the 'edit' command for Script Magic.

This module allows users to edit scripts using a Textual TUI with AI assistance.
"""

import os
import sys
import click
from typing import Dict, Any

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TextArea, Static, Input, ProgressBar, LoadingIndicator
from textual.containers import Container
from textual import events
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.worker import Worker, WorkerState, get_current_worker

from script_magic.mapping_manager import get_mapping_manager
from script_magic.github_integration import (
    download_script_from_gist, 
    GitHubIntegrationError
)
from script_magic.rich_output import console
from script_magic.logger import get_logger
from script_magic.model_providers import ModelManager

# Set up logger
logger = get_logger(__name__)

# Initialize model manager and get default model
model_manager = ModelManager()
DEFAULT_MODEL = model_manager.DEFAULT_MODELS["default"]

class ProgressModal(ModalScreen):
    """A modal screen showing progress for AI operations."""
    
    DEFAULT_CSS = """
    ProgressModal {
        align: center middle;
    }

    #progress-container {
        width: 80%; 
        height: auto;
        background: $surface;
        padding: 1 2;
        border: solid $primary;
        layout: vertical;           /* Ensures vertical stacking and full-width children */
        align-horizontal: center;   /* Centers content horizontally within the container */
    }

    #progress-title {
        width: 100%;
        content-align: center middle;
        text-align: center;
    }

    #progress-message {
        width: 100%;
        text-align: center;
        margin: 1 0;
    }

    #loading-indicator {
        width: 100%;
        content-align: center middle;
        height: 3;
        margin: 1 0;
    }
    """
    
    def __init__(self, title="Processing with AI"):
        super().__init__()
        self.title = title
        self.message = "Please wait while the AI processes your request..."
    
    def compose(self) -> ComposeResult:
        """Compose the progress modal."""
        with Container(id="progress-container"):
            yield Static(self.title, id="progress-title")
            yield Static(self.message, id="progress-message")
            yield LoadingIndicator(id="loading-indicator")
    
    def update_message(self, message: str) -> None:
        """Update the progress message."""
        message_widget = self.query_one("#progress-message", Static)
        message_widget.update(message)
    
    def pulse(self) -> None:
        """No longer needed with LoadingIndicator."""
        pass

class PromptModal(ModalScreen):
    """A modal screen for entering a prompt."""
    
    DEFAULT_CSS = """
    PromptModal {
        align: center middle;
    }
    
    #prompt-container {
        width: 80%;
        height: auto;
        background: #222222;
        padding: 2 4;
        border: solid #444444;
    }
    
    #prompt-title {
        text-align: center;
        width: 100%;
        margin-bottom: 1;
    }
    
    #prompt-input {
        width: 100%;
        margin-bottom: 1;
    }
    
    #button-container {
        width: 100%;
        height: auto;
        align: center middle;
        margin-top: 1;
    }
    
    Button {
        margin-right: 2;
    }
    """
    
    def __init__(self):
        super().__init__()
        self.result = None
    
    def compose(self) -> ComposeResult:
        """Compose the prompt modal."""
        with Container(id="prompt-container"):
            yield Static("Enter your prompt", id="prompt-title")
            yield Input(placeholder="Type your prompt here...", id="prompt-input")
            yield Static("Press ENTER to submit or ESC to cancel", id="button-container")
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle the prompt submission."""
        self.result = event.value
        self.dismiss(True)
    
    def on_key(self, event: events.Key) -> None:
        """Handle key events."""
        if event.key == "escape":
            self.dismiss(False)

class ScriptEditor(App):
    """A Textual app for editing Python scripts."""
    
    ENABLE_COMMAND_PALETTE = False

    CSS = """
    Screen {
        background: #121212;
        layout: vertical;
    }
    
    Vertical {
        height: 100%;
    }
    
    Horizontal {
        height: 1fr;
    }
    
    TextArea {
        height: 1fr;
        border: solid #333333;
        background: #1e1e1e;
        color: #e0e0e0;
        margin: 0 0;
    }
    
    .status-bar {
        height: auto;
        background: #007acc;
        color: white;
        padding: 0 1;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+r", "reload", "Reload"),
        Binding("ctrl+p", "prompt", "Prompt"),
    ]
    
    def __init__(self, script_name: str, script_content: str, gist_id: str, 
                 description: str, mapping_manager: Any, script_info: Dict[str, Any], 
                 model: str = DEFAULT_MODEL):
        """Initialize the editor with script content."""
        super().__init__()
        self.script_name = script_name
        self.script_content = script_content
        self.gist_id = gist_id
        self.description = description
        self.saved = False
        self.original_content = script_content
        self._allow_quit = False
        self.mapping_manager = mapping_manager
        self.script_info = script_info
        self.model = model  # Store the model to use
        # Store metadata for later use
        self.metadata = script_info.get("metadata", {})
        # Store updated description and tags
        self.updated_description = description
        self.updated_tags = []
        # Store AI processing results
        self.ai_results = None
        # Track worker IDs that have shown notifications
        self._notified_workers = set()
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)
        # Use TextArea.code_editor directly which already has line numbers enabled
        yield TextArea.code_editor(self.script_content, language="python", id="editor")
        yield Static(f"File: {self.script_name} | Python Editor", classes="status-bar", id="status-bar")
        yield Footer()
    
    def on_mount(self) -> None:
        """Handle the mount event."""
        try:
            editor = self.query_one("#editor", TextArea)
            editor.focus()
            
            # Configure editor to handle escape sequences properly
            editor.show_line_numbers = True
            
            # Mark the app as fully initialized
            self._initialized = True
        except Exception as e:
            logger.error(f"Error in on_mount: {e}", exc_info=True)
            self._initialized = False
    
    def on_key(self, event: events.Key) -> None:
        """Handle keyboard events for enhanced Python editing."""
        try:
            # Check if the app is fully initialized and editor exists
            if not hasattr(self, "_initialized") or not self._initialized:
                return
                
            # Try to get the editor, but don't crash if it's not there
            try:
                editor = self.query_one("#editor", TextArea)
                if not editor.has_focus:
                    return
                
                # Special handling for arrow keys to prevent escape sequence issues
                if event.key in ("up", "down", "left", "right"):
                    # Let Textual handle these keys normally, don't insert text
                    return
                
                # Add any editor-specific key handling logic here
            except Exception as e:
                # Just log the error and continue
                logger.debug(f"Editor not available during key event: {e}")
                return
        except Exception as e:
            # Catch all exceptions to prevent app crashes
            logger.error(f"Error in on_key: {e}", exc_info=True)
    
    def action_save(self) -> None:
        """Save the script locally"""
        try:
            # Get the current content from the TextArea
            editor = self.query_one("#editor", TextArea)
            updated_content = editor.text
            
            # First, save the content locally
            self.notify("Saving script locally...", timeout=2)
            try:
                local_path = self.mapping_manager.save_script_locally(
                    self.script_name, 
                    updated_content
                )
                logger.info(f"Saved script to {local_path}")
            except Exception as e:
                logger.error(f"Failed to save script locally: {str(e)}", exc_info=True)
                self.notify(f"Error saving locally: {str(e)}", timeout=3, severity="error")
            
            self.notify(f"✓ Script saved successfully!", timeout=3)
            self.saved = True
            
            # Update original content to mark as saved
            self.original_content = updated_content
            self.script_content = updated_content
            
        except Exception as e:
            logger.error(f"Failed to save script: {str(e)}", exc_info=True)
            self.notify(f"Error saving script: {str(e)}", timeout=5, severity="error")
    
    def action_quit(self) -> None:
        """Quit the application."""
        editor = self.query_one("#editor", TextArea)
        if editor.text != self.original_content and not self.saved:
            if self._allow_quit:
                self.exit()
            else:
                self.notify("You have unsaved changes. Press Ctrl+Q again to force quit.", timeout=3)
                # Set a flag to allow quitting on next Ctrl+Q
                self._allow_quit = True
                self.set_timer(3, self._reset_quit_flag)
        else:
            self.exit()
    
    def _reset_quit_flag(self) -> None:
        """Reset the quit confirmation flag."""
        self._allow_quit = False
            
    def action_reload(self) -> None:
        """Reload the script content from local storage if available.""" 
        try:
            # First try to load from local storage
            local_content = self.mapping_manager.load_script_locally(self.script_name)
            
            if local_content:
                editor = self.query_one("#editor", TextArea)
                editor.text = local_content
                self.notify("Script reloaded from local storage", timeout=3)
                return
                
            # If no local content, fall back to original content
            editor = self.query_one("#editor", TextArea)
            if editor.text != self.original_content:
                editor.text = self.original_content
                self.notify("Script reset to original content", timeout=3)
            else:
                self.notify("No changes to reset", timeout=2)
                
        except Exception as e:
            logger.error(f"Failed to reload script: {str(e)}", exc_info=True)
            self.notify(f"Error reloading script: {str(e)}", timeout=3, severity="error")
    
    def action_prompt(self) -> None:
        """Show a prompt dialog to get user input.""" 
        # Start the worker that will show the prompt modal
        self.run_worker(self._show_prompt_modal())
    
    async def _show_prompt_modal(self) -> None:
        """Worker that shows the prompt modal and processes the result.""" 
        prompt_modal = PromptModal()
        result = await self.push_screen(prompt_modal, wait_for_dismiss=True)
        if result and prompt_modal.result:
            prompt_text = prompt_modal.result
            self.notify(f"Processing prompt: {prompt_text[:30]}{'...' if len(prompt_text) > 30 else ''}", timeout=3)
            
            # Process the prompt
            await self.process_prompt(prompt_text)
    
    async def process_prompt(self, prompt: str) -> None:
        """Process the user's prompt using AI to edit the script."""
        try:
            # Get current content from the editor
            editor = self.query_one("#editor", TextArea)
            current_script = editor.text
            
            # Create and show progress modal
            progress_modal = ProgressModal(f"Processing with {self.model}")
            self.push_screen(progress_modal)
            
            # Set up a timer to pulse the progress bar every 0.5 seconds to show activity
            def pulse_progress():
                try:
                    # Check if progress modal is still active
                    if not self.is_screen_active(ProgressModal):
                        return False  # Stop the timer
                    progress_modal.pulse()
                    return True  # Continue the timer
                except Exception as e:
                    logger.debug(f"Error pulsing progress bar: {e}")
                    return False  # Stop the timer on error
            
            # Start the pulse timer
            self.set_interval(0.5, pulse_progress)
            
            # Create a worker to process the AI edit
            def ai_worker():
                try:
                    worker = get_current_worker()
                    # Import inside the function to avoid circular imports
                    from script_magic.ai_integration import edit_script as ai_edit_script
                    
                    if worker.is_cancelled:
                        return None, None, None
                    
                    # Use the AI to edit the script with the specified model
                    edited_script, updated_description, updated_tags = ai_edit_script(
                        current_script, 
                        prompt,
                        model=self.model
                    )
                    return edited_script, updated_description, updated_tags
                except Exception as e:
                    logger.error(f"AI worker error: {str(e)}", exc_info=True)
                    return None, None, None
            
            # Create and run the worker (use thread=True since AI processing is CPU-intensive)
            worker = self.run_worker(ai_worker, thread=True)
            
        except Exception as e:
            # Clean up and reset on error
            try:
                self.dismiss_progress_modal()
            except Exception:
                pass
                
            logger.error(f"Failed to process prompt with AI: {str(e)}", exc_info=True)
            self.notify(f"Error processing with AI: {str(e)}", timeout=5, severity="error")

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker state changes."""
        worker = event.worker
        worker_id = id(worker)
        
        # Get the worker name to identify which process is running
        worker_name = getattr(worker, 'name', '')
        
        # Handle specific workers differently
        if worker_name == '_show_prompt_modal':
            # This is the prompt modal worker, no need to modify UI elements
            return
            
        if worker.state == WorkerState.RUNNING:
            # Only show notification if we haven't already notified for this worker
            if worker_id not in self._notified_workers:
                # Update the progress modal if it exists
                try:
                    progress_modal = self.get_screen(ProgressModal)
                    progress_modal.update_message("AI is generating code based on your prompt...")
                except Exception as e:
                    logger.debug(f"Could not update progress modal: {e}")
                
                self._notified_workers.add(worker_id)
        
        elif worker.state == WorkerState.SUCCESS:
            # Worker completed successfully
            
            # Only update status bar if we have one (not during modal operations)
            try:
                status_bar = self.query_one("#status-bar", Static)
                status_bar.update(f"File: {self.script_name} | Python Editor")
            except Exception as e:
                logger.debug(f"Status bar not available: {e}")
            
            result = worker.result
            if result:
                edited_script, updated_description, updated_tags = result
                
                if edited_script:
                    # Store the generated script and metadata in instance variables
                    # so they can be accessed after dismissing the modal
                    self.ai_generated_script = edited_script
                    self.updated_description = updated_description
                    self.updated_tags = updated_tags
                    
                    # Make sure we know the content has changed
                    self.saved = False
                    
                    # Set progress to 100% complete to show success
                    try:
                        progress_modal = self.get_screen(ProgressModal)
                        progress_bar = progress_modal.query_one("#progress-bar", ProgressBar)
                        progress_bar.update(total=1.0, progress=1.0)  # Set to 100% complete
                        progress_modal.update_message("✓ Changes generated successfully!")
                        # Pause briefly so the user can see the completion message
                        self.set_timer(1.5, self._update_editor_after_modal)
                    except Exception as e:
                        logger.debug(f"Could not update progress modal: {e}")
                        self._update_editor_after_modal()
                        
                else:
                    # Dismiss the progress modal with a message
                    try:
                        progress_modal = self.get_screen(ProgressModal)
                        progress_bar = progress_modal.query_one("#progress-bar", ProgressBar)
                        progress_bar.update(total=1.0, progress=1.0)  # Set to 100% complete
                        progress_modal.update_message("AI did not suggest any changes")
                        self.set_timer(1.5, self.dismiss_progress_modal)
                    except Exception as e:
                        logger.debug(f"Could not update progress modal: {e}")
                        self.dismiss_progress_modal()
                    
                    self.notify("AI did not suggest any changes to your script", timeout=3)
                
            # Clean up the worker tracking
            if worker_id in self._notified_workers:
                self._notified_workers.remove(worker_id)
                
        elif worker.state in (WorkerState.ERROR, WorkerState.CANCELLED):
            # Only update status bar if we have one (not during modal operations)
            try:
                status_bar = self.query_one("#status-bar", Static)
                status_bar.update(f"File: {self.script_name} | Python Editor")
            except Exception as e:
                logger.debug(f"Status bar not available: {e}")
            
            # Update progress modal with error message and show as failed
            try:
                progress_modal = self.get_screen(ProgressModal)
                progress_bar = progress_modal.query_one("#progress-bar", ProgressBar)
                # Set progress to 0 but with a total to show no progress was made
                progress_bar.update(total=1.0, progress=0)
                
                if worker.state == WorkerState.ERROR:
                    error_msg = str(worker.error) if worker.error else "Unknown error"
                    progress_modal.update_message(f"Error: {error_msg}")
                else:
                    progress_modal.update_message("Operation was cancelled")
                self.set_timer(2, self.dismiss_progress_modal)
            except Exception as e:
                logger.debug(f"Could not update progress modal: {e}")
                self.dismiss_progress_modal()
            
            if worker.state == WorkerState.ERROR:
                # Worker encountered an error
                error = worker.error
                logger.error(f"Worker error: {error}", exc_info=True)
                self.notify(f"Error in AI processing: {str(error)}", timeout=5, severity="error")
            else:
                # Worker was cancelled
                self.notify("AI processing was cancelled", timeout=2)
                
            # Clean up the worker tracking
            if worker_id in self._notified_workers:
                self._notified_workers.remove(worker_id)
    
    def _update_editor_after_modal(self) -> None:
        """Update the editor with AI-generated content after dismissing the modal."""
        # First dismiss the progress modal
        self.dismiss_progress_modal()
        
        # Now that we're back to the main screen, try to update the editor
        try:
            # Check if we have AI-generated content to apply
            if hasattr(self, "ai_generated_script") and self.ai_generated_script:
                # Verify the editor exists before updating
                if self.query("TextArea#editor"):
                    editor = self.query_one("#editor", TextArea)
                    editor.text = self.ai_generated_script
                    
                    # Notify the user of successful update
                    self.notify("✓ Script updated with AI-generated changes!", timeout=3)
                else:
                    logger.warning("Editor not available when trying to update with AI changes")
                    self.notify("⚠️ Could not update editor - please try again", timeout=3, severity="warning")
        except Exception as e:
            logger.error(f"Error updating editor after modal: {str(e)}", exc_info=True)
            self.notify(f"Error updating editor: {str(e)}", timeout=3, severity="error")

    def is_screen_active(self, screen_class) -> bool:
        """Check if a screen of the given class is currently active."""
        try:
            self.get_screen(screen_class)
            return True
        except Exception:
            return False
            
    def dismiss_progress_modal(self) -> None:
        """Helper method to dismiss the progress modal."""
        try:
            progress_modal = self.get_screen(ProgressModal)
            self.pop_screen()
        except Exception as e:
            logger.debug(f"Could not dismiss progress modal: {e}")

def edit_script(script_name: str, model: str = DEFAULT_MODEL) -> bool:
    """
    Edit a Python script using Textual TUI.
    
    Args:
        script_name: Name of the script to edit
        model: The model to use for AI editing
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Opening Python script '{script_name}' for editing using model: {model}")
    
    try:
        # Get the mapping manager and look up the script
        mapping_manager = get_mapping_manager()
        script_info = mapping_manager.lookup_script(script_name)
        
        if not script_info:
            console.print(f"[bold red]Error:[/bold red] Script '{script_name}' not found")
            return False
        
        # First try to load from local storage
        try:
            content = mapping_manager.load_script_locally(script_name)
            if content:
                console.print(f"[green]Using locally stored version of '{script_name}'[/green]")
            else:
                content = None
        except AttributeError as e:
            logger.error(f"Error loading locally: {str(e)}")
            console.print("[yellow]Warning: Local script storage not available.[/yellow]")
            content = None
        
        # If not found locally, get from GitHub
        if not content:
            # Get the Gist ID
            gist_id = script_info.get("gist_id")
            if not gist_id:
                console.print(f"[bold red]Error:[/bold red] No Gist ID found for script '{script_name}'")
                return False
            
            # Download the script content from GitHub
            console.print(f"[bold blue]Downloading Python script '{script_name}' from GitHub...[/bold blue]")
            try:
                content, metadata = download_script_from_gist(gist_id)
                # Try to save to local storage for future use
                try:
                    mapping_manager.save_script_locally(script_name, content)
                except AttributeError:
                    logger.warning("Local script storage not available")
            except GitHubIntegrationError as e:
                console.print(f"[yellow]Warning: Could not download from GitHub: {str(e)}[/yellow]")
                console.print("[yellow]Please fix GitHub integration or save a local copy.[/yellow]")
                # Create an empty Python script template if none exists
                content = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
Script: {script_name}
Description: Add description here
\"\"\"

def main():
    \"\"\"Main function\"\"\" 
    print("Hello from {script_name}!")

if __name__ == "__main__":
    main()
""".format(script_name=script_name)
        
        # Get description
        description = ""
        if "metadata" in script_info and "description" in script_info["metadata"]:
            description = script_info["metadata"]["description"]
        if not description:
            description = f"Python script: {script_name}"
            
        gist_id = script_info.get("gist_id", "")
        
        # Start the Textual app
        app = ScriptEditor(
            script_name=script_name,
            script_content=content,
            gist_id=gist_id,
            description=description,
            mapping_manager=mapping_manager,
            script_info=script_info,
            model=model  # Pass the model to the editor
        )
        
        console.print(f"[bold blue]Opening Python editor for '{script_name}' using model '{model}'...[/bold blue]")

        app.run()
        
        # Check if the script was saved
        if getattr(app, "saved", False):
            console.print(f"[bold green]✓ Python script '{script_name}' saved successfully![/bold green]")
            return True
        else:
            console.print(f"[yellow]Editing of script '{script_name}' was cancelled.[/yellow]")
            return False
        
    except GitHubIntegrationError as e:
        console.print(f"[bold red]GitHub Error:[/bold red] {str(e)}")
        logger.error(f"GitHub integration error: {str(e)}")
        return False
    except Exception as e:
        console.print(f"[bold red]Error editing script:[/bold red] {str(e)}")
        logger.error(f"Script editing error: {str(e)}", exc_info=True)
        return False

@click.command()
@click.argument('script_name')
@click.option('--model', '-m', default=DEFAULT_MODEL, 
             help=f'Model to use for AI assistance. Available choices: {", ".join(model_manager.DEFAULT_MODELS.keys())}. '
                  f'Default: {DEFAULT_MODEL}')
def cli(script_name: str, model: str) -> None:
    """
    Edit an existing Python script in a text editor.
    
    SCRIPT_NAME: Name of the script to edit
    """
    # Check environment variables
    if not os.getenv("MY_GITHUB_PAT"):
        console.print("[bold red]Error:[/bold red] MY_GITHUB_PAT environment variable is not set")
        sys.exit(1)
    
    # Run the edit command
    success = edit_script(script_name, model)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    cli()