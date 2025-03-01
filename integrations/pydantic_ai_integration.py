"""
PydanticAI integration for script generation.

This module provides functions to generate Python scripts using PydanticAI,
with support for interactive refinement and PEP 723 metadata inclusion.
"""
import os
import re
from typing import Optional, Tuple, Dict
from datetime import datetime

from pydantic_ai import Agent
from pydantic import BaseModel

# Import Rich utilities
from rich.console import Console
from rich.syntax import Syntax
try:
    from ..utils.rich_output import display_code, display_heading
except ImportError:
    # Fallback for direct module execution
    import sys
    import pathlib
    sys.path.append(str(pathlib.Path(__file__).parent.parent))
    from utils.rich_output import display_code, display_heading

# Check for required environment variables
if not os.getenv("OPENAI_API_KEY"):
    print("Warning: OPENAI_API_KEY environment variable not set. Some features may not work correctly.")

# Create a model for the script generation
class ScriptResult(BaseModel):
    """Model for script generation results."""
    code: str
    explanation: str
    additional_notes: Optional[str] = None

# Set up the agent
script_agent = Agent(
    'openai:gpt-4o-mini',
    result_type=ScriptResult,
    system_prompt="""
    You are a Python script generator. When given a prompt, you will:
    1. Generate a complete, working Python script
    2. Include clear inline comments
    3. Follow Python best practices and PEP 8
    4. Include PEP 723 compliant metadata as comments at the top of the file
    5. Keep the code focused and efficient
    
    The metadata should follow this format (PEP 723):
    ```python
    # /// script
    # description = "Brief description of what the script does"
    # authors = ["Script-Magic AI Generator"]
    # date = "YYYY-MM-DD"
    # requires-python = ">=3.9"
    # dependencies = [
    #     # List any required packages here, for example:
    #     # "requests>=2.25.1",
    # ]
    # tags = ["generated", "script-magic"]
    # ///
    
    # Generated from the prompt: "<prompt text>"
    ```
    
    For each script, provide:
    1. The complete Python code with PEP 723 metadata
    2. A brief explanation of how the script works
    3. Any additional notes or caveats the user should be aware of
    """
)

def add_metadata_if_missing(code: str, prompt: str) -> str:
    """
    Ensures the script has PEP 723 compliant metadata.
    If metadata is missing, adds it to the top of the script.
    """
    # Check if PEP 723 metadata already exists
    if re.search(r"^# /// script[\s\S]*?# ///", code, re.MULTILINE):
        return code
        
    # Create metadata block
    today = datetime.now().strftime("%Y-%m-%d")
    description = prompt.strip().split('.')[0] if '.' in prompt else prompt.strip()
    metadata = f"""# /// script
# description = "{description}"
# authors = ["Script-Magic AI Generator"]
# date = "{today}"
# requires-python = ">=3.9"
# dependencies = []
# tags = ["generated", "script-magic"]
# ///

# Generated from the prompt: "{prompt.strip()}"

"""
    # Add metadata to the top of the script
    return metadata + code

def generate_script(prompt: str, user_vars: Optional[Dict[str, str]] = None) -> str:
    """
    Generate a Python script based on the provided prompt.
    
    Args:
        prompt: The prompt describing what the script should do
        user_vars: Optional variables to replace in the prompt
        
    Returns:
        The generated Python script as a string
    """
    try:
        # Replace variables in the prompt if provided
        if user_vars:
            for var, value in user_vars.items():
                placeholder = f"{{{{{var}}}}}"
                prompt = prompt.replace(placeholder, value)
        
        # Run the agent to generate the script
        result = script_agent.run_sync(prompt)
        
        # Extract the generated code and ensure metadata is included
        code = result.data.code
        code = add_metadata_if_missing(code, prompt)
        
        return code
    
    except Exception as e:
        return f"""# /// script
# description = "Error generating script"
# authors = ["Script-Magic AI Generator"]
# date = "{datetime.now().strftime("%Y-%m-%d")}"
# tags = ["generated", "error"]
# ///

# Failed to generate script from prompt: "{prompt.strip()}"
# Error: {str(e)}

# Error occurred during script generation
print("Error: Failed to generate script")
"""

def interactive_refinement(prompt: str, user_vars: Optional[Dict[str, str]] = None) -> str:
    """
    Generate a script with interactive refinement.
    
    Args:
        prompt: The initial prompt describing what the script should do
        user_vars: Optional variables to replace in the prompt
        
    Returns:
        The final, accepted script as a string
    """
    current_script = generate_script(prompt, user_vars)
    
    while True:
        display_heading("Generated Script", style="bold green")
        display_code(current_script, language="python", line_numbers=True)
        
        user_input = input("\nDo you want to refine the script? (y/n): ").strip().lower()
        
        if user_input != 'y':
            return current_script
        
        refinement = input("\nPlease describe what changes you want: ")
        full_prompt = f"{prompt}\n\nRevision request: {refinement}"
        current_script = generate_script(full_prompt, user_vars)

def process_prompt(prompt: str, user_vars: Optional[Dict[str, str]] = None, interactive: bool = False) -> str:
    """
    Process a prompt to generate a Python script.
    
    Args:
        prompt: The prompt describing what the script should do
        user_vars: Optional variables to replace in the prompt
        interactive: Whether to enable interactive refinement
        
    Returns:
        The generated Python script as a string
    """
    if interactive:
        return interactive_refinement(prompt, user_vars)
    else:
        return generate_script(prompt, user_vars)

def display_script(script: str, title: Optional[str] = "Generated Script"):
    """
    Display a script with syntax highlighting using Rich.
    
    Args:
        script: The script text to display
        title: Optional title for the displayed script
    """
    display_code(script, language="python", line_numbers=True, title=title)

if __name__ == "__main__":
    # Example usage
    test_prompt = "Create a script to list files in the current directory sorted by size."
    script = process_prompt(test_prompt, interactive=True)
    display_heading("Final Script", style="bold blue")
    display_code(script, language="python", line_numbers=True)
