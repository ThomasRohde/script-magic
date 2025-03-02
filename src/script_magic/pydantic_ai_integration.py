"""
PydanticAI integration for script generation.

This module provides functions to generate Python scripts using PydanticAI,
with support for interactive refinement and PEP 723 metadata inclusion.
"""
import os
import re
from typing import Optional, Dict
from datetime import datetime

from pydantic_ai import Agent
from pydantic import BaseModel

try:
    from script_magic.rich_output import display_code, display_heading
except ImportError:
    # Fallback for direct module execution
    import sys
    import pathlib
    sys.path.append(str(pathlib.Path(__file__).parent.parent))
    from script_magic.rich_output import display_code, display_heading

# Check for required environment variables
if not os.getenv("OPENAI_API_KEY"):
    print("Warning: OPENAI_API_KEY environment variable not set. Some features may not work correctly.")

# Create a model for the script generation
class ScriptResult(BaseModel):
    """Model for script generation results."""
    code: str
    description: str
    tags: list[str] = ["generated", "script-magic"]
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
    
    IMPORTANT: For any parameters in double curly braces like {{parameter_name}}, create a script that 
    accepts command line arguments. For example, if you see {{prefix}} in the prompt, the script should 
    accept a command line parameter named "prefix".

    Use argparse or click to properly parse command line arguments in a user-friendly way.
    Always implement proper error handling for missing or incorrect arguments.
    
    For each script, provide:
    1. The complete Python code with PEP 723 metadata
    2. A brief explanation of how the script works
    3. Any additional notes or caveats the user should be aware of
    4. Create tags for the script that are relevant to the script's functionality
    """
)

def add_metadata_if_missing(code: str, prompt: str, description: str = "", tags: list[str] = None) -> str:
    """
    Ensures the script has PEP 723 compliant metadata.
    If metadata is missing, adds it to the top of the script.
    
    Args:
        code: The script code
        prompt: The original prompt
        description: Description from the AI result
        tags: Tags from the AI result
    """
    # Check if PEP 723 metadata already exists
    if re.search(r"^# /// script[\s\S]*?# ///", code, re.MULTILINE):
        return code
    
    # Use provided description or fallback to prompt
    if not description:
        description = prompt.strip().split('.')[0] if '.' in prompt else prompt.strip()
    
    # Use provided tags or defaults
    if not tags:
        tags = ["generated", "script-magic"]
    
    # Format tags as a string list
    tags_str = ", ".join([f'"{tag}"' for tag in tags])
    
    # Create metadata block
    today = datetime.now().strftime("%Y-%m-%d")
    metadata = f"""# /// script
# description = "{description}"
# authors = ["Script-Magic AI Generator"]
# date = "{today}"
# requires-python = ">=3.9"
# dependencies = []
# tags = [{tags_str}]
# ///

# Generated from the prompt: "{prompt.strip()}"

"""
    # Add metadata to the top of the script
    return metadata + code

def extract_metadata_tags(script: str) -> list:
    """
    Extract tags from the PEP 723 metadata in the script.
    
    Args:
        script: The script text containing PEP 723 metadata
        
    Returns:
        A list of tags extracted from the metadata
    """
    # Default tags if none are found
    default_tags = ["generated", "script-magic"]
    
    # Look for tags in the PEP 723 metadata - more permissive pattern
    tags_pattern = r'#\s*tags\s*=\s*\[(.*?)\]'
    match = re.search(tags_pattern, script, re.DOTALL)
    
    if not match:
        return default_tags
    
    # Extract and clean up the tags
    tags_str = match.group(1).strip()
    tags = []
    
    # Parse the tags from the list format - handle different quote styles
    for tag in re.findall(r'["\']([^"\']+)["\']', tags_str):
        tags.append(tag)
    
    # Also catch tags without quotes but separated by commas
    if not tags:
        for tag in tags_str.split(','):
            clean_tag = tag.strip()
            if clean_tag and not clean_tag.startswith('#'):  # Skip comments
                tags.append(clean_tag)
    
    # If no tags were extracted, use defaults
    return tags if tags else default_tags

def generate_script(prompt: str, user_vars: Optional[Dict[str, str]] = None) -> tuple[str, str, list[str]]:
    """
    Generate a Python script based on the provided prompt.
    
    Args:
        prompt: The prompt describing what the script should do
        user_vars: Optional variables to include in the script (not replacing in prompt)
        
    Returns:
        A tuple containing (code, description, tags)
    """
    try:
        # Run the agent to generate the script
        result = script_agent.run_sync(prompt)
        
        # Extract the generated code and ensure metadata is included
        code = result.data.code
        description = result.data.description
        tags = result.data.tags
        
        # Ensure code has metadata
        code = add_metadata_if_missing(code, prompt, description, tags)
        
        return code, description, tags
    
    except Exception as e:
        error_code = f"""# /// script
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
        return error_code, "Error generating script", ["generated", "error"]

def interactive_refinement(prompt: str, user_vars: Optional[Dict[str, str]] = None) -> tuple[str, str, list[str]]:
    """
    Generate a script with interactive refinement.
    
    Args:
        prompt: The initial prompt describing what the script should do
        user_vars: Optional variables to replace in the prompt
        
    Returns:
        A tuple containing (code, description, tags)
    """
    current_script, description, tags = generate_script(prompt, user_vars)
    
    while True:
        display_heading("Generated Script", style="bold green")
        display_code(current_script, language="python", line_numbers=True)
        
        user_input = input("\nDo you want to refine the script? (y/n): ").strip().lower()
        
        if user_input != 'y':
            return current_script, description, tags
        
        refinement = input("\nPlease describe what changes you want: ")
        full_prompt = f"{prompt}\n\nRevision request: {refinement}"
        current_script, description, tags = generate_script(full_prompt, user_vars)

def process_prompt(prompt: str, user_vars: Optional[Dict[str, str]] = None, interactive: bool = False) -> tuple[str, str, list[str]]:
    """
    Process a prompt to generate a Python script.
    
    Args:
        prompt: The prompt describing what the script should do
        user_vars: Optional variables to replace in the prompt
        interactive: Whether to enable interactive refinement
        
    Returns:
        A tuple containing (code, description, tags)
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
    script, description, tags = process_prompt(test_prompt, interactive=True)
    display_heading("Final Script", style="bold blue")
    display_code(script, language="python", line_numbers=True)
