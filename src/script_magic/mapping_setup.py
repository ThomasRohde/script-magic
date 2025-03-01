# Utility to set up mapping file with GitHub integration

import os
import sys
import logging
from typing import Tuple
import click

from script_magic.mapping_manager import MappingManager, DEFAULT_MAPPING_FILE, GIST_ID_FILE
from script_magic.github_gist_finder import select_best_mapping_gist
from script_magic.github_integration import GitHubIntegrationError, get_mapping_from_gist

# Set up logger
logger = logging.getLogger(__name__)

# Track if we've already run setup
_setup_completed = False

def setup_mapping() -> Tuple[MappingManager, bool]:
    """
    Set up the mapping system, with GitHub integration if available.
    
    Returns:
        Tuple[MappingManager, bool]: A tuple containing the mapping manager and 
        a boolean indicating whether GitHub integration was successful
    """
    global _setup_completed
    
    # Skip if we've already run setup in this session
    if _setup_completed:
        # Just return the existing mapping manager
        return MappingManager(), True
    
    # Initialize the mapping manager
    mapping_manager = MappingManager()
    github_integration_success = False
    
    try:
        # CASE 1: Both local mapping and Gist ID exist (normal operation)
        if os.path.exists(DEFAULT_MAPPING_FILE) and os.path.exists(GIST_ID_FILE):
            logger.info("Mapping file and Gist ID found - system already initialized")
            github_integration_success = True
        
        # CASE 2: Local mapping exists but no Gist ID
        elif os.path.exists(DEFAULT_MAPPING_FILE) and not os.path.exists(GIST_ID_FILE):
            logger.info("Local mapping exists but no Gist ID - looking for existing Gist")
            
            # Try to find if user has a mapping Gist already
            gist_id = select_best_mapping_gist()
            
            if gist_id:
                # Found a mapping Gist - ask user which to keep
                logger.info(f"Found existing mapping Gist: {gist_id}")
                print("Found existing mapping Gist on GitHub.")
                choice = input("Use GitHub version instead of local? (y/n): ").lower().strip()
                
                if choice in ('y', 'yes'):
                    # Use GitHub version
                    mapping_manager.gist_id = gist_id
                    mapping_manager._save_gist_id(gist_id)
                    mapping_manager._sync_from_github()
                    logger.info("Using GitHub mapping version")
                else:
                    # Use local version but save Gist ID for future syncs
                    mapping_manager.gist_id = gist_id
                    mapping_manager._save_gist_id(gist_id)
                    # Will update GitHub with our local version on next sync
                    logger.info("Using local mapping version - will update GitHub on next sync")
                    
                github_integration_success = True
            else:
                # No mapping Gist found - will create one on first sync
                logger.info("No existing mapping Gist found - will create one on next sync")
                print("No existing mapping Gist found. Will create one when you run a sync operation.")
        
        # CASE 3: No local mapping but Gist ID exists (unlikely but possible)
        elif not os.path.exists(DEFAULT_MAPPING_FILE) and os.path.exists(GIST_ID_FILE):
            logger.info("Gist ID exists but no local mapping - downloading from GitHub")
            
            # Load the Gist ID and sync from GitHub
            with open(GIST_ID_FILE, 'r') as f:
                gist_id = f.read().strip()
                
            if gist_id:
                mapping_manager.gist_id = gist_id
                success = mapping_manager._sync_from_github()
                if success:
                    logger.info(f"Successfully synced mapping from Gist {gist_id}")
                    github_integration_success = True
                else:
                    # Failed to sync - create empty mapping file
                    logger.warning(f"Failed to sync from Gist {gist_id} - creating empty mapping")
                    mapping_manager._ensure_mapping_file_exists()
            else:
                # Empty Gist ID file - create empty mapping
                logger.warning("Empty Gist ID file - creating empty mapping")
                mapping_manager._ensure_mapping_file_exists()
        
        # CASE 4: No local mapping and no Gist ID (first-time user)
        else:
            logger.info("No local mapping or Gist ID - looking for existing Gist")
            
            # Try to find if user has a mapping Gist already
            gist_id = select_best_mapping_gist()
            
            if gist_id:
                # Found a mapping Gist - use it
                logger.info(f"Found existing mapping Gist: {gist_id}")
                print(f"Found existing mapping Gist on GitHub. Using it.")
                
                mapping_manager.gist_id = gist_id
                mapping_manager._save_gist_id(gist_id)
                success = mapping_manager._sync_from_github()
                
                if success:
                    logger.info(f"Successfully synced mapping from Gist {gist_id}")
                    github_integration_success = True
                else:
                    # Failed to sync - create empty mapping file
                    logger.warning(f"Failed to sync from Gist {gist_id} - creating empty mapping")
                    mapping_manager._ensure_mapping_file_exists()
            else:
                # No mapping Gist found - create empty mapping
                logger.info("No existing mapping Gist found - creating empty mapping")
                print("Creating new local script mapping...")
                mapping_manager._ensure_mapping_file_exists()
                print("Local mapping created. Will sync to GitHub on first script creation.")
    
    except GitHubIntegrationError as e:
        logger.error(f"GitHub integration error during setup: {str(e)}")
        github_integration_success = False
        print(f"GitHub integration failed: {str(e)}")
        print("Continuing with local mapping only.")
        
        # Ensure we have a local mapping file even if GitHub integration fails
        if not os.path.exists(DEFAULT_MAPPING_FILE):
            mapping_manager._ensure_mapping_file_exists()
    
    except Exception as e:
        logger.error(f"Unexpected error during mapping setup: {str(e)}")
        github_integration_success = False
        
        # Ensure we have a local mapping file even if there's an error
        if not os.path.exists(DEFAULT_MAPPING_FILE):
            mapping_manager._ensure_mapping_file_exists()
    
    _setup_completed = True
    return mapping_manager, github_integration_success

if __name__ == "__main__":
    # When run directly, perform the setup
    try:
        mapping_manager, success = setup_mapping()
        if success:
            print("Mapping setup complete with GitHub integration.")
        else:
            print("Mapping setup complete, but GitHub integration failed.")
    except KeyboardInterrupt:
        print("\nSetup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Setup failed: {str(e)}")
        sys.exit(1)
