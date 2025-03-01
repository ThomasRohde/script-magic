# Utility to set up mapping file with GitHub integration

import os
import sys
import logging
from typing import Tuple

from script_magic.mapping_manager import MappingManager, DEFAULT_MAPPING_FILE, GIST_ID_FILE
from script_magic.github_gist_finder import select_best_mapping_gist
from script_magic.github_integration import GitHubIntegrationError, get_mapping_from_gist

# Set up logger
logger = logging.getLogger(__name__)

def setup_mapping() -> Tuple[MappingManager, bool]:
    """
    Set up the mapping system, with GitHub integration if available.
    
    Returns:
        Tuple[MappingManager, bool]: A tuple containing the mapping manager and 
        a boolean indicating whether GitHub integration was successful
    """
    # Initialize the mapping manager
    mapping_manager = MappingManager()
    github_integration_success = False
    
    # If the mapping file already exists and there's a Gist ID, we're good
    if os.path.exists(DEFAULT_MAPPING_FILE) and os.path.exists(GIST_ID_FILE):
        logger.info("Mapping file and Gist ID already exist")
        return mapping_manager, True
    
    # If we don't have a Gist ID but the mapping file exists:
    # 1. Try to find an existing mapping Gist
    # 2. If found, sync with it
    # 3. If not, create a new Gist with our local mapping
    try:
        if not os.path.exists(GIST_ID_FILE):
            gist_id = select_best_mapping_gist()
            
            if gist_id:
                logger.info(f"Found existing mapping Gist: {gist_id}")
                
                # Save the Gist ID
                with open(GIST_ID_FILE, 'w') as f:
                    f.write(gist_id)
                mapping_manager.gist_id = gist_id
                
                # If we already have a mapping file, ask which one to use
                if os.path.exists(DEFAULT_MAPPING_FILE):
                    print("Found both local mapping file and GitHub Gist mapping.")
                    choice = input("Use GitHub version? (y/n): ").lower().strip()
                    
                    if choice in ('y', 'yes'):
                        # Get mapping from GitHub
                        mapping_manager._sync_from_github()
                    else:
                        # Push local to GitHub
                        mapping_manager.sync_mapping()
                else:
                    # No local mapping, just sync from GitHub
                    mapping_manager._sync_from_github()
                
                github_integration_success = True
            else:
                logger.info("No existing mapping Gist found, will create new one on first sync")
                
                # Ensure we have a local mapping file
                if not os.path.exists(DEFAULT_MAPPING_FILE):
                    # Initialize an empty mapping
                    mapping_manager._ensure_mapping_file_exists()
                
                # On first sync, this will create a new Gist
                mapping_manager.sync_mapping()
                github_integration_success = True
    
    except GitHubIntegrationError as e:
        logger.error(f"GitHub integration error during setup: {str(e)}")
        github_integration_success = False
        print(f"GitHub integration failed: {str(e)}")
        print("Continuing with local mapping only.")
    
    except Exception as e:
        logger.error(f"Unexpected error during mapping setup: {str(e)}")
        github_integration_success = False
    
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
