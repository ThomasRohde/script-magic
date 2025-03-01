# This file will search for existing mapping Gists on GitHub

import os
import logging
from typing import Optional, List, Dict, Any
from github import Github, GithubException

from script_magic.github_integration import get_github_client, GitHubIntegrationError

# Set up logger
logger = logging.getLogger(__name__)

def find_mapping_gists() -> List[Dict[str, Any]]:
    """
    Search for potential mapping Gists that belong to the authenticated user.
    
    Returns:
        List of dictionaries with Gist information (id, description, updated_at)
        
    Raises:
        GitHubIntegrationError: If GitHub API access fails
    """
    try:
        client = get_github_client()
        user = client.get_user()
        
        # Get all gists for the authenticated user
        gists = user.get_gists()
        
        mapping_gists = []
        for gist in gists:
            # Look for gists that match our criteria (having mapping.json file)
            if "mapping.json" in gist.files:
                mapping_gists.append({
                    "id": gist.id,
                    "description": gist.description,
                    "updated_at": gist.updated_at.isoformat() if gist.updated_at else None,
                    "created_at": gist.created_at.isoformat() if gist.created_at else None,
                })
        
        logger.info(f"Found {len(mapping_gists)} potential mapping Gists")
        return mapping_gists
    
    except GithubException as e:
        logger.error(f"GitHub API error while searching for mapping Gists: {e}")
        raise GitHubIntegrationError(f"Failed to search for mapping Gists: {e}")
    except Exception as e:
        logger.error(f"Unexpected error searching for mapping Gists: {e}")
        raise GitHubIntegrationError(f"Unexpected error searching for mapping Gists: {e}")

def select_best_mapping_gist() -> Optional[str]:
    """
    Find and select the most appropriate mapping Gist.
    Strategy: return the most recently updated mapping Gist.
    
    Returns:
        str: ID of the selected Gist, or None if no suitable Gist found
    """
    try:
        gists = find_mapping_gists()
        
        if not gists:
            logger.info("No existing mapping Gists found")
            return None
        
        # Sort by updated_at (most recent first)
        sorted_gists = sorted(
            gists, 
            key=lambda g: g.get("updated_at", ""), 
            reverse=True
        )
        
        # Return the ID of the most recently updated Gist
        best_gist_id = sorted_gists[0]["id"]
        logger.info(f"Selected mapping Gist {best_gist_id} (most recently updated)")
        return best_gist_id
    
    except Exception as e:
        logger.error(f"Error selecting best mapping Gist: {e}")
        return None
