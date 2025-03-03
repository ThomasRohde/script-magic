import re
import ast

def parse_pep723_metadata(file_content: str):
    """
    Parses the inline PEP 723 metadata from a Python script.
    
    The metadata block should be delimited as follows:
      # /// script
      # key = value
      # key2 = [
      #   "item1",
      #   "item2",
      # ]
      # ///
    
    Returns:
      A tuple (metadata_dict, corrected_metadata_str)
      
      - metadata_dict: A dictionary with the parsed metadata.
      - corrected_metadata_str: A string with a corrected version of the metadata block.
      
    Raises:
      ValueError if the metadata block is not found.
    """
    # Regex to capture everything between the start and end markers.
    pattern = re.compile(
        r"^#\s*///\s*script\s*(.*?)^#\s*///\s*$",
        re.MULTILINE | re.DOTALL
    )
    match = pattern.search(file_content)
    if not match:
        raise ValueError("PEP 723 metadata block not found.")
    
    block = match.group(1)
    lines = block.splitlines()
    
    metadata = {}
    current_key = None
    current_value_lines = []
    
    for line in lines:
        # Remove the comment marker and extra whitespace.
        stripped_line = line.strip().lstrip("#").strip()
        if not stripped_line:
            continue
        
        # If not in the middle of a multi-line value and the line contains '='
        if '=' in stripped_line and current_key is None:
            parts = stripped_line.split("=", 1)
            key = parts[0].strip()
            value = parts[1].strip()
            # If the value starts with '[' but does not end with ']', it's a multi-line list.
            if value.startswith('[') and not value.endswith(']'):
                current_key = key
                current_value_lines = [value]
            else:
                try:
                    evaluated = ast.literal_eval(value)
                except Exception:
                    evaluated = value  # Fallback to raw string if evaluation fails.
                metadata[key] = evaluated
        elif current_key is not None:
            # Accumulate lines for a multi-line value.
            current_value_lines.append(stripped_line)
            if stripped_line.endswith(']'):
                full_value = " ".join(current_value_lines)
                try:
                    evaluated = ast.literal_eval(full_value)
                except Exception:
                    evaluated = full_value
                metadata[current_key] = evaluated
                current_key = None
                current_value_lines = []
        else:
            # Skip lines that do not match the expected pattern.
            continue

    # Reconstruct a corrected metadata block.
    corrected_lines = ["# /// script"]
    for key, value in metadata.items():
        if isinstance(value, list):
            corrected_lines.append(f"# {key} = [")
            for item in value:
                corrected_lines.append(f"#   {repr(item)},")
            corrected_lines.append("# ]")
        else:
            corrected_lines.append(f"# {key} = {repr(value)}")
    corrected_lines.append("# ///")
    corrected_metadata_str = "\n".join(corrected_lines)
    
    return metadata, corrected_metadata_str

def update_script_with_corrected_metadata(file_content: str) -> str:
    """
    Replaces the PEP 723 metadata block in the provided script with a corrected version,
    and returns the entire updated script.
    """
    # First, get the corrected metadata block.
    _, corrected_metadata_str = parse_pep723_metadata(file_content)
    
    # Use regex to substitute the entire original metadata block with the corrected one.
    full_pattern = re.compile(
        r"^#\s*///\s*script\s*.*?^#\s*///\s*$",
        re.MULTILINE | re.DOTALL
    )
    updated_content = full_pattern.sub(corrected_metadata_str, file_content)
    return updated_content

# Example usage:
if __name__ == "__main__":
    sample_script = '''\
# /// script
# requires-python = ">=3.11"
# dependencies = [ "requests >=2.25.1",
#   "numpy>=1.19.5",
# ]
#///
import requests
import numpy as np

def hello():
    print("Hello, world!")

hello()
'''
    try:
        updated_script = update_script_with_corrected_metadata(sample_script)
        print("Updated script:")
        print(updated_script)
    except ValueError as err:
        print("Error:", err)
