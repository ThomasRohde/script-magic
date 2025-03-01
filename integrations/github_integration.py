# This file will handle GitHub Gist uploads, downloads, and mapping file sync

import os
import json
import logging
from typing import Dict, Optional, Tuple, Any
from github import Github, GithubException
from github.Gist import Gist

# Set up logger
logger = logging.getLogger(__name__)

class GitHubIntegrationError(Exception):
    """Custom exception for GitHub integration errors."""
    pass

def get_github_client() -> Github:
    """
    Create and return an authenticated GitHub client using the PAT from environment variables.
    
    Returns:
        Github: Authenticated GitHub client
        
    Raises:
        GitHubIntegrationError: If GITHUB_PAT is not set or authentication fails
    """
    github_token = os.environ.get("GITHUB_PAT")
    
    if not github_token:
        logger.error("GITHUB_PAT environment variable not set")
        raise GitHubIntegrationError("GitHub Personal Access Token not found. Please set the GITHUB_PAT environment variable.")
    
    try:
        client = Github(github_token)
        # Test authentication by getting the authenticated user
        user = client.get_user().login
        logger.info(f"Successfully authenticated as {user}")
        return client
    except GithubException as e:
        logger.error(f"GitHub authentication failed: {e}")
        raise GitHubIntegrationError(f"GitHub authentication failed: {e}")

def upload_script_to_gist(script_name: str, script_content: str, description: str = None) -> str:
    """
    Upload a script to GitHub Gists.
    
    Args:
        script_name: Name of the script (will be used as filename with .py extension)
        script_content: Content of the script as a string
        description: Optional description for the Gist
        
    Returns:
        str: ID of the created Gist
        
    Raises:
        GitHubIntegrationError: If Gist creation fails
    """
    if not description:
        description = f"SM Tool script: {script_name}"
    
    filename = f"{script_name}.py"
    files = {filename: {"content": script_content}}
    
    try:
        client = get_github_client()
        gist = client.get_user().create_gist(True, files, description)
        logger.info(f"Created Gist {gist.id} for script '{script_name}'")
        return gist.id
    except GithubException as e:
        logger.error(f"Failed to create Gist for script '{script_name}': {e}")
        raise GitHubIntegrationError(f"Failed to upload script to GitHub Gist: {e}")

def download_script_from_gist(gist_id: str) -> Tuple[str, Dict[str, Any]]:
    """
    Download a script from a GitHub Gist by its ID.
    
    Args:
        gist_id: The ID of the Gist to download
        
    Returns:
        Tuple[str, Dict[str, Any]]: Tuple containing the script content and metadata
        
    Raises:
        GitHubIntegrationError: If Gist retrieval fails or contains no files
    """
    try:
        client = get_github_client()
        gist = client.get_gist(gist_id)
        
        if not gist.files:
            logger.error(f"Gist {gist_id} does not contain any files")
            raise GitHubIntegrationError(f"Gist {gist_id} does not contain any files")
        
        # Get the first Python file in the Gist (assuming it's our script)
        py_files = [file for file in gist.files.values() 
                   if file.filename.endswith('.py')]
        
        if not py_files:
            logger.error(f"No Python files found in Gist {gist_id}")
            raise GitHubIntegrationError(f"No Python files found in Gist {gist_id}")
        
        script_file = py_files[0]
        content = script_file.content
        
        # Create metadata
        metadata = {
            "gist_id": gist_id,
            "filename": script_file.filename,
            "description": gist.description,
            "updated_at": gist.updated_at.isoformat() if gist.updated_at else None,
            "created_at": gist.created_at.isoformat() if gist.created_at else None,
        }
        
        logger.info(f"Successfully downloaded script from Gist {gist_id}")
        return content, metadata
    
    except GithubException as e:
        logger.error(f"Failed to download script from Gist {gist_id}: {e}")
        raise GitHubIntegrationError(f"Failed to download script from Gist: {e}")

def sync_mapping_file(mapping_data: dict, mapping_gist_id: Optional[str] = None) -> str:
    """
    Sync the local mapping data with a GitHub Gist.
    If mapping_gist_id is provided, update that Gist.
    If not provided, create a new Gist for the mapping.
    
    Args:
        mapping_data: Dictionary containing mapping data
        mapping_gist_id: Optional ID of an existing mapping Gist
        
    Returns:
        str: ID of the Gist (either new or updated)
        
    Raises:
        GitHubIntegrationError: If syncing fails
    """
    client = get_github_client()
    mapping_content = json.dumps(mapping_data, indent=2)
    
    try:
        if mapping_gist_id:
            # Update existing Gist
            try:
                gist = client.get_gist(mapping_gist_id)
                gist.edit(
                    description="SM Tool Script Mapping File",
                    files={"mapping.json": {"content": mapping_content}}
                )
                logger.info(f"Updated mapping file in Gist {mapping_gist_id}")
                return mapping_gist_id
            except GithubException as e:
                logger.error(f"Failed to update mapping Gist {mapping_gist_id}: {e}")
                raise GitHubIntegrationError(f"Failed to update mapping Gist: {e}")
        else:
            # Create new Gist
            try:
                files = {"mapping.json": {"content": mapping_content}}
                gist = client.get_user().create_gist(
                    True,  # public=False (i.e., private Gist)
                    files,
                    "SM Tool Script Mapping File"
                )
                logger.info(f"Created new mapping file Gist with ID {gist.id}")
                return gist.id
            except GithubException as e:
                logger.error(f"Failed to create new mapping Gist: {e}")
                raise GitHubIntegrationError(f"Failed to create mapping Gist: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during mapping sync: {e}")
        raise GitHubIntegrationError(f"Unexpected error during mapping sync: {e}")

def get_mapping_from_gist(mapping_gist_id: str) -> dict:
    """
    Retrieve the mapping data from a GitHub Gist.
    
    Args:
        mapping_gist_id: ID of the Gist containing the mapping file
        
    Returns:
        dict: The mapping data as a dictionary
        
    Raises:
        GitHubIntegrationError: If retrieval fails
    """
    try:
        client = get_github_client()
        gist = client.get_gist(mapping_gist_id)
        
        if "mapping.json" not in gist.files:
            logger.error(f"Gist {mapping_gist_id} does not contain mapping.json")
            raise GitHubIntegrationError(f"Gist {mapping_gist_id} does not contain mapping.json")
        
        content = gist.files["mapping.json"].content
        mapping_data = json.loads(content)
        logger.info(f"Successfully retrieved mapping data from Gist {mapping_gist_id}")
        return mapping_data
    
    except GithubException as e:
        logger.error(f"Failed to retrieve mapping from Gist {mapping_gist_id}: {e}")
        raise GitHubIntegrationError(f"Failed to retrieve mapping from Gist: {e}")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in mapping file from Gist {mapping_gist_id}: {e}")
        raise GitHubIntegrationError(f"Invalid JSON in mapping file: {e}")
