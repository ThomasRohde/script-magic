# Developer Specification for the Python Script Manager (SM)

This document outlines a comprehensive, developer-ready specification for a command-line Python tool (hereafter referred to as “SM”) that integrates the following key features:

- **Script Execution:** Use the [uv package manager](https://astral.sh/uv) to execute scripts stored in GitHub Gists.
- **Script Creation:** Generate Python scripts via PydanticAI using a command-line prompt and inline metadata (PEP 723 compliant) supported by uv.
- **Mapping File Management:** Maintain a local mapping file that tracks script names to GitHub Gist IDs (with associated metadata) and automatically sync it with a specific GitHub Gist.
- **Interactive Refinement:** Provide an optional preview mode (using Rich formatting) with interactive conversation via the PydanticAI LLM for iterative changes before finalizing script creation.
- **GitHub Integration:** Leverage GitHub’s API to handle Gist creation and versioning of the mapping file.
- **CLI Interface:** Built with Click command groups for intuitive command structure.

---

## Table of Contents

- [Overview](#overview)
- [Functional Requirements](#functional-requirements)
- [Non-Functional Requirements](#non-functional-requirements)
- [Architecture Overview](#architecture-overview)
- [Components & Workflow](#components--workflow)
  - [SM Create Command](#sm-create-command)
  - [SM Run Command](#sm-run-command)
- [Data Handling](#data-handling)
- [Error Handling Strategies](#error-handling-strategies)
- [Dependencies & Environment](#dependencies--environment)
- [Additional Implementation Details](#additional-implementation-details)
- [Appendix: Command Examples](#appendix-command-examples)

---

## Overview

The SM tool is designed to simplify and automate script management by integrating with:
- **uv package manager:** For fast dependency resolution and execution of Python scripts with inline metadata.
- **PydanticAI:** For generating Python scripts from natural language prompts.
- **GitHub Gists & Git API:** For storing and versioning generated scripts and mapping file.
- **Rich:** For beautifully formatted preview output in interactive mode.
- **Click:** For a structured command-line interface.

This tool allows users to quickly create, preview, refine, and run Python scripts stored in GitHub Gists while maintaining a synchronized mapping file.

---

## Functional Requirements

1. **Script Creation (`sm create`):**
   - Accepts a script name and a prompt (e.g., `sm create script-name "Create a script to list all gists with names starting with {{prefix}}"`).
   - Uses PydanticAI to generate a Python script based on the provided prompt.
   - Supports a preview mode using a `-p`/`--preview` flag:
     - Displays the generated script using Rich formatting.
     - Prompts the user for interactive confirmation or further modifications via conversation with the PydanticAI LLM.
   - Upon confirmation, uploads the script to GitHub Gist.
   - Updates the local mapping file with:
     - Script name
     - Gist ID
     - Timestamp
     - Any other metadata as needed
   - Automatically syncs the local mapping file with a specific remote GitHub Gist using the Git API.

2. **Script Execution (`sm run`):**
   - Accepts a script name and parameters (e.g., `sm run script-name prefix=gist`).
   - Looks up the script in the local mapping file to obtain the corresponding GitHub Gist ID.
   - Optionally fetches the latest version of the script from GitHub Gist.
   - Executes the script using `uv run`, leveraging uv’s fast environment management and support for inline script metadata (PEP 723).
   - Passes command-line parameters to the script as needed.

3. **Mapping File Versioning:**
   - The local mapping file (e.g., stored as JSON at a standard location like `~/.sm/mapping.json`) maintains the mapping between script names and Gist IDs.
   - Uses GitHub API integration to version and sync the mapping file automatically after any changes.

4. **GitHub Authentication:**
   - Uses a GitHub Personal Access Token (PAT) read from a default environment variable (`GITHUB_PAT`).

---

## Non-Functional Requirements

- **Performance:** Execution and dependency resolution via uv should leverage its Rust-based speed, ensuring fast script runs.
- **Usability:** Command-line interface should be intuitive with clear commands and options.
- **Extensibility:** Code structure should allow easy additions or modifications to support new features or integrations.
- **Robustness:** Proper error handling for network issues, GitHub API failures, uv execution errors, and LLM responses.
- **Security:** Secure handling of API keys and sensitive data through environment variables and secure storage practices.
- **Logging & Debugging:** Include logging for critical operations and error tracking.

---

## Architecture Overview

The application is structured as a CLI tool built with Click, with two primary command groups:
- **create:** For generating, previewing, refining, and uploading scripts.
- **run:** For fetching and executing scripts.

The tool integrates multiple subsystems:
- **Script Generation Module:** Interfaces with PydanticAI to generate scripts.
- **Preview & Interactive Refinement Module:** Uses Rich for formatting previews and an interactive prompt to iterate with PydanticAI.
- **GitHub Integration Module:** Handles Gist creation, script uploads, and mapping file sync via the Git API.
- **Execution Module:** Leverages uv (using `uv run`) to execute downloaded scripts with inline metadata.
- **Mapping File Manager:** Reads/writes a local JSON file for script-to-Gist mappings and handles versioning via Git API.

---

## Components & Workflow

### SM Create Command

1. **Input Parsing:**
   - Accepts arguments: script name and prompt.
   - Optional flag: `-p` / `--preview`.

2. **Script Generation:**
   - Invoke PydanticAI with the given prompt to generate a Python script.
   - Embed inline metadata in the generated script following uv’s default (PEP 723 compliant) approach.

3. **Preview Mode (if enabled):**
   - Display the generated script using Rich formatting.
   - Ask: “Do you have any changes?” and allow interactive refinement via a conversation with the PydanticAI LLM.
   - Repeat until the user accepts the script.

4. **Uploading and Mapping:**
   - Upload the finalized script to GitHub Gist.
   - Update the local mapping file with the script name, Gist ID, timestamp, etc.
   - Automatically commit and push the mapping file update to the configured remote Gist using Git API.

### SM Run Command

1. **Mapping Lookup:**
   - Read the local mapping file to get the Gist ID corresponding to the script name.
   - Optionally fetch the latest script version from GitHub if needed.

2. **Script Execution:**
   - Execute the script using `uv run`, ensuring that:
     - The script’s inline metadata is processed per uv’s standard.
     - Command-line parameters (e.g., `prefix=gist`) are passed to the script.

3. **Output Handling:**
   - Display the output from the script execution on the console.

---

## Data Handling

- **Local Mapping File:**
  - Format: JSON.
  - Location: Standard configuration directory (e.g., `~/.sm/mapping.json`).
  - Fields include:
    - `script_name`
    - `gist_id`
    - `created_at` (timestamp)
    - Additional metadata (if required).

- **GitHub Gist Content:**
  - Each uploaded script is stored as a Gist.
  - Inline metadata is embedded in the script file (handled by uv inline script metadata support).

- **Synchronization:**
  - The mapping file is automatically synced with a specific remote GitHub Gist using Git API calls, ensuring version control and consistency between local and remote records.

---

## Error Handling Strategies

- **GitHub API Errors:**
  - Detect and log network failures, authentication issues, and API rate limits.
  - Provide user-friendly error messages and suggest retry strategies.

- **PydanticAI Generation Failures:**
  - Validate the response from the LLM.
  - If the generated script fails validation (via Pydantic), prompt the user to refine the prompt interactively.

- **UV Execution Failures:**
  - Capture errors from `uv run` and display clear diagnostic information.
  - Optionally fall back to a manual execution mode if uv fails.

- **Mapping File Sync Issues:**
  - If automatic Git sync fails, log the error and provide instructions to manually reconcile the mapping file.
  - Implement retry logic with exponential backoff for transient network errors.

- **Interactive Confirmation:**
  - In preview mode, if the user declines the preview or requests changes, re-initiate the interactive conversation with the PydanticAI LLM until the script meets the user’s approval.

---

## Dependencies & Environment

- **Core Libraries:**
  - `click`: For CLI command grouping and argument parsing.
  - `rich`: For console output formatting and interactive previews.
  - `uv`: For script execution and environment management.
  - `pydantic-ai`: For generating Python scripts based on natural language prompts.
  - `PyGithub` (or similar GitHub API library): For interfacing with GitHub Gists and syncing mapping file.
  
- **Other Utilities:**
  - Standard libraries: `json`, `os`, `datetime`, `logging`, etc.
  
- **Environment Variables:**
  - `GITHUB_PAT`: GitHub Personal Access Token (default variable name).

- **Python Version:**
  - Minimum Python 3.9 (as required by uv and pydantic-ai).

---

## Additional Implementation Details

- **Project Structure:**
  - `cli.py`: Main entry point using Click to define `sm` command group.
  - `commands/create.py`: Implements the `sm create` command logic.
  - `commands/run.py`: Implements the `sm run` command logic.
  - `pydantic_ai_integration.py`: Module to interact with PydanticAI for script generation and interactive refinement.
  - `github_integration.py`: Module handling GitHub Gist uploads, downloads, and mapping file sync.
  - `mapping_manager.py`: Module for reading/writing the local mapping file.
  - `utils.py`: Helper functions (logging, formatting, error handling).

- **Execution Flow:**
  - The CLI starts in `cli.py` and dispatches commands based on user input.
  - Each command module calls its respective integration module.
  - Errors are logged centrally and meaningful error messages are presented to the user.

- **Inline Script Metadata:**
  - Use uv’s default approach for inline metadata per PEP 723. No additional modifications are required.

- **Interactive Conversation:**
  - When preview mode is enabled and the user requests changes, launch an interactive session with the PydanticAI LLM.
  - Continue the conversation until the user confirms acceptance of the generated script.

- **Logging & Debugging:**
  - Configure logging at startup.
  - Use appropriate log levels (INFO, DEBUG, ERROR) throughout the application.
  - Optionally add a verbose flag to increase output verbosity during development.

---

## Appendix: Command Examples

### Create Script with Preview

```bash
sm create my-script "Create a script to list all gists with names starting with {{prefix}}" --preview
