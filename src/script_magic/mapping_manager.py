# This file will manage the local mapping file (read/write operations)

import json
import os
import datetime

from typing import Dict, List, Optional, Any

# Import the logger from our logger module
from script_magic.logger import get_logger
# Import GitHub integration for gist operations
from script_magic.github_integration import (
    sync_mapping_file, 
    get_mapping_from_gist, 
    GitHubIntegrationError
)

logger = get_logger(__name__)

# Default paths and constants
DEFAULT_MAPPING_DIR = os.path.expanduser("~/.sm")
DEFAULT_MAPPING_FILE = os.path.join(DEFAULT_MAPPING_DIR, "mapping.json")
GIST_ID_FILE = os.path.join(DEFAULT_MAPPING_DIR, "gist_id.txt")

class MappingManager:
    def __init__(self, mapping_file: str = DEFAULT_MAPPING_FILE):
        """
        Initialize the mapping manager with the path to the mapping file.
        
        Args:
            mapping_file: Path to the mapping file (default: ~/.sm/mapping.json)
        """
        self.mapping_file = mapping_file
        self.gist_id = None
        self._ensure_mapping_file_exists()
        self._load_gist_id()
    
    def _load_gist_id(self) -> None:
        """Load the GitHub Gist ID from the gist_id file if it exists."""
        try:
            if os.path.exists(GIST_ID_FILE):
                with open(GIST_ID_FILE, 'r') as f:
                    self.gist_id = f.read().strip()
                logger.debug(f"Loaded mapping Gist ID: {self.gist_id}")
        except Exception as e:
            logger.error(f"Failed to load Gist ID: {str(e)}")
            self.gist_id = None
    
    def _save_gist_id(self, gist_id: str) -> None:
        """Save the GitHub Gist ID to a file."""
        try:
            mapping_dir = os.path.dirname(GIST_ID_FILE)
            if not os.path.exists(mapping_dir):
                os.makedirs(mapping_dir)
                
            with open(GIST_ID_FILE, 'w') as f:
                f.write(gist_id)
            self.gist_id = gist_id
            logger.debug(f"Saved mapping Gist ID: {gist_id}")
        except Exception as e:
            logger.error(f"Failed to save Gist ID: {str(e)}")
    
    def _ensure_mapping_file_exists(self) -> None:
        """
        Ensure that the mapping file and its directory exist.
        Create a new empty mapping file if none exists.
        """
        mapping_dir = os.path.dirname(self.mapping_file)
        
        try:
            # Create the directory if it doesn't exist
            if not os.path.exists(mapping_dir):
                logger.info(f"Creating mapping directory: {mapping_dir}")
                os.makedirs(mapping_dir)
            
            # Create the mapping file if it doesn't exist
            if not os.path.exists(self.mapping_file):
                logger.info(f"Creating new empty mapping file: {self.mapping_file}")
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
            with open(self.mapping_file, 'r', encoding='utf-8') as f:
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
            with open(self.mapping_file, 'w', encoding='utf-8') as f:
                json.dump(mapping_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error writing to mapping file: {str(e)}")
            raise
    
    def _sync_to_github(self) -> None:
        """
        Sync the local mapping file to GitHub.
        If no gist_id exists, create a new gist.
        """
        try:
            mapping_data = self._read_mapping()
            gist_id = sync_mapping_file(mapping_data, self.gist_id)
            
            if not self.gist_id:
                self._save_gist_id(gist_id)
                logger.info(f"Created new mapping Gist with ID: {gist_id}")
            else:
                logger.info(f"Updated mapping Gist with ID: {gist_id}")
            
            # Update the last_synced timestamp
            mapping_data["last_synced"] = datetime.datetime.now().isoformat()
            self._write_mapping(mapping_data)
            
        except GitHubIntegrationError as e:
            logger.error(f"GitHub integration error while syncing mapping: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error syncing mapping to GitHub: {str(e)}")
            raise
    
    def _sync_from_github(self) -> bool:
        """
        Download and update the local mapping file from GitHub.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.gist_id:
            logger.warning("No Gist ID available for mapping sync")
            return False
        
        try:
            mapping_data = get_mapping_from_gist(self.gist_id)
            self._write_mapping(mapping_data)
            logger.info(f"Successfully synced mapping from GitHub Gist {self.gist_id}")
            return True
        except GitHubIntegrationError as e:
            logger.error(f"GitHub integration error while loading mapping: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error syncing mapping from GitHub: {str(e)}")
            return False
    
    def add_script(self, script_name: str, gist_id: str, metadata: Optional[Dict[str, Any]] = None, sync: bool = True) -> None:
        """
        Add a new script entry to the mapping file.
        
        Args:
            script_name: Name of the script
            gist_id: ID of the GitHub Gist
            metadata: Additional metadata for the script (optional)
            sync: Whether to automatically sync to GitHub after adding (default: True)
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
            
            # Automatically sync to GitHub if requested
            if sync:
                try:
                    self.sync_mapping()
                    logger.info(f"Automatically synced mapping to GitHub after adding script '{script_name}'")
                except Exception as e:
                    logger.error(f"Failed to auto-sync mapping after adding script '{script_name}': {str(e)}")
                    
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
        Sync the mapping file with GitHub Gist.
        - If no gist_id is available, create a new gist
        - If gist_id exists, update the existing gist
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Sync to GitHub
            self._sync_to_github()
            logger.info("Mapping successfully synced to GitHub")
            return True
        except Exception as e:
            logger.error(f"Error syncing mapping: {str(e)}")
            return False

    def initialize_from_github(self) -> bool:
        """
        Try to initialize the mapping from GitHub.
        This can be used during first-time setup to search for and use
        an existing mapping Gist.
        
        Returns:
            bool: True if successful, False if no GitHub mapping was found
        """
        # If we already have a Gist ID, just sync from it
        if self.gist_id:
            return self._sync_from_github()
        
        # This would be implemented in a separate function to search for mapping Gists
        # For now, just return False since we can't find a Gist without an ID
        logger.warning("No existing mapping Gist ID found. Use sync_mapping() to create one.")
        return False

    def get_script_info(self, script_name: str) -> dict:
        """
        Get information about a specific script.
        
        Args:
            script_name: Name of the script
            
        Returns:
            dict: Script information or None if not found
        """
        scripts = self.list_scripts()
        for script in scripts:
            if script["name"] == script_name:
                return script
        return None
    
    def remove_script(self, script_name: str, sync: bool = True) -> bool:
        """
        Remove a script from the local mapping.
        
        Args:
            script_name: Name of the script to remove
            sync: Whether to automatically sync to GitHub after removal (default: True)
            
        Returns:
            bool: True if script was found and removed, False otherwise
        """
        # Load current mapping
        mapping = self._read_mapping()
        
        # Check if script exists
        if script_name not in mapping.get('scripts', {}):
            return False
            
        # Remove script entry
        del mapping['scripts'][script_name]
        
        # Save updated mapping
        self._write_mapping(mapping)
        
        # Automatically sync to GitHub if requested
        if sync:
            try:
                self.sync_mapping()
                logger.info(f"Automatically synced mapping to GitHub after removing script '{script_name}'")
            except Exception as e:
                logger.error(f"Failed to auto-sync mapping after removing script '{script_name}': {str(e)}")
                # We still return True as the local removal was successful
        
        return True

    def sync_with_github(self) -> bool:
        """
        Synchronize local mapping with GitHub Gists.
        
        Returns:
            bool: True if sync was successful, False otherwise
        """
        if not self.github_integration:
            logger.error("GitHub integration not available for synchronization")
            return False
            
        try:
            logger.debug("Starting GitHub sync")
            # Get all gists from GitHub
            gists = self.github_integration.list_gists()
            
            if not gists:
                logger.debug("No gists found on GitHub")
                return True  # No gists to sync is not an error
                
            # Track changes for logging
            added_scripts = []
            updated_scripts = []
            
            # Update local mapping with GitHub data
            for gist in gists:
                # Look for our script identifier in the description
                if "[script-magic]" in gist.description:
                    script_name = gist.description.split("[script-magic] ")[1].strip()
                    script_id = gist.id
                    
                    if script_name not in self.mapping:
                        # New script found on GitHub
                        self.mapping[script_name] = script_id
                        added_scripts.append(script_name)
                    elif self.mapping[script_name] != script_id:
                        # Script exists but ID has changed
                        self.mapping[script_name] = script_id
                        updated_scripts.append(script_name)
            
            # Save updated mapping
            self._save_mapping()
            
            # Log results
            if added_scripts:
                logger.info(f"Added {len(added_scripts)} scripts from GitHub: {', '.join(added_scripts)}")
            if updated_scripts:
                logger.info(f"Updated {len(updated_scripts)} scripts from GitHub: {', '.join(updated_scripts)}")
                
            logger.debug("GitHub sync completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to sync with GitHub: {str(e)}")
            return False

# Helper functions for easier import/use
_mapping_manager_instance = None

def get_mapping_manager(mapping_file: str = DEFAULT_MAPPING_FILE) -> MappingManager:
    """Get a MappingManager instance with the given mapping file."""
    global _mapping_manager_instance
    if _mapping_manager_instance is None:
        # Try to import here to avoid circular imports
        try:
            from script_magic.mapping_setup import setup_mapping
            _mapping_manager_instance, _ = setup_mapping()
        except ImportError:
            # Fall back to direct instantiation if setup_mapping is not available
            _mapping_manager_instance = MappingManager(mapping_file)
    return _mapping_manager_instance
