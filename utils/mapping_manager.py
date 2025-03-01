# This file will manage the local mapping file (read/write operations)

import json
import os
import datetime

from typing import Dict, List, Optional, Any

# Import the logger from our logger module
from utils.logger import get_logger

logger = get_logger(__name__)

# Default paths and constants
DEFAULT_MAPPING_DIR = os.path.expanduser("~/.sm")
DEFAULT_MAPPING_FILE = os.path.join(DEFAULT_MAPPING_DIR, "mapping.json")

class MappingManager:
    def __init__(self, mapping_file: str = DEFAULT_MAPPING_FILE):
        """
        Initialize the mapping manager with the path to the mapping file.
        
        Args:
            mapping_file: Path to the mapping file (default: ~/.sm/mapping.json)
        """
        self.mapping_file = mapping_file
        self._ensure_mapping_file_exists()
    
    def _ensure_mapping_file_exists(self) -> None:
        """Ensure that the mapping file and its directory exist."""
        mapping_dir = os.path.dirname(self.mapping_file)
        
        try:
            # Create the directory if it doesn't exist
            if not os.path.exists(mapping_dir):
                logger.info(f"Creating mapping directory: {mapping_dir}")
                os.makedirs(mapping_dir)
            
            # Create the mapping file if it doesn't exist
            if not os.path.exists(self.mapping_file):
                logger.info(f"Creating new mapping file: {self.mapping_file}")
                self._write_mapping({
                    "scripts": {},
                    "last_synced": None
                })
        except Exception as e:
            logger.error(f"Failed to initialize mapping file: {str(e)}")
            raise
    
    def _read_mapping(self) -> Dict[str, Any]:
        """
        Read the mapping file and return its contents.
        
        Returns:
            Dict containing the mapping data
        """
        try:
            with open(self.mapping_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Mapping file not found at {self.mapping_file}")
            return {"scripts": {}, "last_synced": None}
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in mapping file {self.mapping_file}")
            return {"scripts": {}, "last_synced": None}
        except Exception as e:
            logger.error(f"Error reading mapping file: {str(e)}")
            raise
    
    def _write_mapping(self, mapping_data: Dict[str, Any]) -> None:
        """
        Write the mapping data to the mapping file.
        
        Args:
            mapping_data: Dictionary containing the mapping data
        """
        try:
            with open(self.mapping_file, 'w') as f:
                json.dump(mapping_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error writing to mapping file: {str(e)}")
            raise
    
    def add_script(self, script_name: str, gist_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a new script entry to the mapping file.
        
        Args:
            script_name: Name of the script
            gist_id: ID of the GitHub Gist
            metadata: Additional metadata for the script (optional)
        """
        if metadata is None:
            metadata = {}
        
        try:
            mapping_data = self._read_mapping()
            
            # Create entry with timestamp
            script_entry = {
                "gist_id": gist_id,
                "created_at": datetime.datetime.now().isoformat(),
                **metadata
            }
            
            # Add or update the script entry
            mapping_data["scripts"][script_name] = script_entry
            
            # Write the updated mapping back to file
            self._write_mapping(mapping_data)
            logger.info(f"Added/updated script '{script_name}' with Gist ID '{gist_id}'")
        except Exception as e:
            logger.error(f"Failed to add script '{script_name}': {str(e)}")
            raise
    
    def lookup_script(self, script_name: str) -> Optional[Dict[str, Any]]:
        """
        Look up a script by name in the mapping file.
        
        Args:
            script_name: Name of the script to look up
            
        Returns:
            Dictionary with script info or None if not found
        """
        try:
            mapping_data = self._read_mapping()
            script_data = mapping_data.get("scripts", {}).get(script_name)
            
            if script_data:
                logger.debug(f"Found script '{script_name}' with Gist ID '{script_data.get('gist_id')}'")
                return script_data
            else:
                logger.warning(f"Script '{script_name}' not found in mapping file")
                return None
        except Exception as e:
            logger.error(f"Error looking up script '{script_name}': {str(e)}")
            return None
    
    def list_scripts(self) -> List[Dict[str, Any]]:
        """
        Get a list of all scripts in the mapping file.
        
        Returns:
            List of dictionaries containing script info
        """
        try:
            mapping_data = self._read_mapping()
            scripts = mapping_data.get("scripts", {})
            
            result = []
            for name, data in scripts.items():
                result.append({
                    "name": name,
                    **data
                })
            
            logger.debug(f"Retrieved {len(result)} scripts from mapping file")
            return result
        except Exception as e:
            logger.error(f"Error listing scripts: {str(e)}")
            return []
    
    def delete_script(self, script_name: str) -> bool:
        """
        Delete a script from the mapping file.
        
        Args:
            script_name: Name of the script to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            mapping_data = self._read_mapping()
            
            if script_name in mapping_data.get("scripts", {}):
                del mapping_data["scripts"][script_name]
                self._write_mapping(mapping_data)
                logger.info(f"Deleted script '{script_name}' from mapping file")
                return True
            else:
                logger.warning(f"Cannot delete: script '{script_name}' not found")
                return False
        except Exception as e:
            logger.error(f"Error deleting script '{script_name}': {str(e)}")
            return False
    
    def sync_mapping(self) -> bool:
        """
        Sync the mapping file with remote storage (e.g., GitHub Gist).
        This is a placeholder for actual sync implementation.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # This would be implemented to sync with GitHub
            # For now, just update the last_synced timestamp
            mapping_data = self._read_mapping()
            mapping_data["last_synced"] = datetime.datetime.now().isoformat()
            self._write_mapping(mapping_data)
            
            logger.info("Updated mapping sync timestamp")
            logger.warning("Note: Actual GitHub sync not yet implemented")
            return True
        except Exception as e:
            logger.error(f"Error syncing mapping: {str(e)}")
            return False

# Helper functions for easier import/use
def get_mapping_manager(mapping_file: str = DEFAULT_MAPPING_FILE) -> MappingManager:
    """Get a MappingManager instance with the given mapping file."""
    return MappingManager(mapping_file)
