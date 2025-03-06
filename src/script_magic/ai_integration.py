"""
Instructor integration for script generation.

This module provides functions to generate Python scripts using Instructor and LiteLLM,
with support for interactive refinement and PEP 723 metadata inclusion.
"""
import os
import re
from typing import Optional, Dict, Tuple
from datetime import datetime
from script_magic.pep723 import update_script_with_corrected_metadata
import instructor
from litellm import completion
from pydantic import BaseModel, Field

try:
    from script_magic.rich_output import display_code, display_heading
except ImportError:
    # Fallback for direct module execution
    import sys
    import pathlib
    sys.path.append(str(pathlib.Path(__file__).parent.parent))
    from script_magic.rich_output import display_code, display_heading

# Default model to use if none specified
# DEFAULT_MODEL = "anthropic/claude-3-7-sonnet-20250219"
DEFAULT_MODEL = "openai/gpt-4o-mini"
# DEFAULT_MODEL = "openai/gpt-4o"

# Create a model for the script generation
class ScriptResult(BaseModel):
    """Model for script generation results."""
    code: str = Field(
        description="The complete Python code of the generated script, including PEP 723 metadata"
    )
    description: str = Field(
        description="A brief description of what the script does"
    )
    tags: list[str] = Field(
        default=["generated", "script-magic"],
        description="Tags categorizing the script's functionality and origin"
    )

# Set up the Instructor client with LiteLLM
client = instructor.from_litellm(completion)

# System prompts for generation and editing
SCRIPT_GENERATION_PROMPT = """
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
2. A brief description of what the script does
3. Relevant tags for the script's functionality
"""

SCRIPT_EDIT_PROMPT = """
You are a Python script editor. When given an existing script and modification instructions, you will:
1. Modify the script according to the instructions while preserving its structure
2. Keep or improve the clarity of inline comments
3. Follow Python best practices and PEP 8
4. Preserve the existing PEP 723 metadata, only updating it if necessary
5. Keep the code focused and efficient

For each script edit, provide:
1. The complete updated Python code with PEP 723 metadata
2. A brief description of the modified script
3. Updated tags for the script that are relevant to the script's functionality

When editing:
- Maintain the script's original purpose while implementing the requested changes
- Preserve existing functionality unless explicitly asked to change it
- Update the PEP 723 metadata date to the current date
- Add an "edited" tag to the metadata if not already present
"""

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
    code = update_script_with_corrected_metadata(code)
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

def generate_script(prompt: str, user_vars: Optional[Dict[str, str]] = None, model: str = DEFAULT_MODEL) -> tuple[str, str, list[str]]:
    """
    Generate a Python script based on the provided prompt.
    
    Args:
        prompt: The prompt describing what the script should do
        user_vars: Optional variables to include in the script (not replacing in prompt)
        model: The model to use for generation (default is defined by DEFAULT_MODEL)
        
    Returns:
        A tuple containing (code, description, tags)
    """
    try:
        # Use Instructor with LiteLLM to generate the script
        result = client.chat.completions.create(
            model=model,  # Use the specified model
            messages=[
                {"role": "system", "content": SCRIPT_GENERATION_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_model=ScriptResult
        )
        
        # Extract the generated code and ensure metadata is included
        code = result.code
        description = result.description
        tags = result.tags
        
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

def edit_script(script: str, instructions: str, model: str = DEFAULT_MODEL) -> tuple[str, str, list[str]]:
    """
    Edit an existing Python script based on the provided instructions.
    
    Args:
        script: The original script to modify
        instructions: Instructions describing what changes to make
        model: The model to use for editing (default is defined by DEFAULT_MODEL)
        
    Returns:
        A tuple containing (updated_code, description, tags)
    """
    try:
        # Construct a proper prompt that includes both the script and instructions
        prompt = f"""Below is an existing Python script that needs to be modified:

```python
{script}
```

Please modify the script according to these instructions:
{instructions}

Return the complete modified script maintaining all necessary PEP 723 metadata.
"""
        # Use Instructor with LiteLLM to edit the script
        result = client.chat.completions.create(
            model=model,  # Use the specified model
            messages=[
                {"role": "system", "content": SCRIPT_EDIT_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_model=ScriptResult
        )
        
        # Extract the edited code and metadata
        edited_code = result.code
        description = result.description
        tags = result.tags
        
        # Ensure code has metadata and update the date
        if "edited" not in tags:
            tags.append("edited")
        edited_code = add_metadata_if_missing(edited_code, instructions, description, tags)
        
        # Update the date in metadata
        today = datetime.now().strftime("%Y-%m-%d")
        edited_code = re.sub(
            r'(#\s*date\s*=\s*")[^"]+(")(\s*)', 
            r'\g<1>' + today + r'\g<2>\g<3>', 
            edited_code
        )
        
        return edited_code, description, tags
    
    except Exception as e:
        error_code = f"""# /// script
# description = "Error editing script"
# authors = ["Script-Magic AI Generator"]
# date = "{datetime.now().strftime("%Y-%m-%d")}"
# tags = ["edited", "error"]
# ///

{script}

# Error: Failed to apply edits - {str(e)}
"""
        return error_code, "Error editing script", ["edited", "error"]

def interactive_refinement(prompt: str, user_vars: Optional[Dict[str, str]] = None, model: str = DEFAULT_MODEL) -> tuple[str, str, list[str]]:
    """
    Generate a script with interactive refinement.
    
    Args:
        prompt: The initial prompt describing what the script should do
        user_vars: Optional variables to replace in the prompt
        model: The model to use for generation (default is defined by DEFAULT_MODEL)
        
    Returns:
        A tuple containing (code, description, tags)
    """
    current_script, description, tags = generate_script(prompt, user_vars, model)
    
    while True:
        display_heading("Generated Script", style="bold green")
        display_code(current_script, language="python", line_numbers=True)
        
        user_input = input("\nDo you want to refine the script? (y/n): ").strip().lower()
        
        if user_input != 'y':
            return current_script, description, tags
        
        refinement = input("\nPlease describe what changes you want: ")
        full_prompt = f"{prompt}\n\nRevision request: {refinement}"
        current_script, description, tags = generate_script(full_prompt, user_vars, model)

def process_prompt(prompt: str, user_vars: Optional[Dict[str, str]] = None, 
                  interactive: bool = False, model: str = DEFAULT_MODEL) -> tuple[str, str, list[str]]:
    """
    Process a prompt to generate a Python script.
    
    Args:
        prompt: The prompt describing what the script should do
        user_vars: Optional variables to replace in the prompt
        interactive: Whether to enable interactive refinement
        model: The model to use for generation (default is defined by DEFAULT_MODEL)
        
    Returns:
        A tuple containing (code, description, tags)
    """
    if interactive:
        return interactive_refinement(prompt, user_vars, model)
    else:
        return generate_script(prompt, user_vars, model)

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
    
    # Example of script editing
    edit_instructions = "Add an option to filter files by extension"
    edited_script, new_description, new_tags = edit_script(script, edit_instructions)
    display_heading("Edited Script", style="bold green")
    display_code(edited_script, language="python", line_numbers=True)
