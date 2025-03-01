# SM Tool TODO Checklist

This checklist details every step for building the SM tool. Each task builds on the previous ones to ensure incremental progress and complete integration.

---

## Project Setup & Structure
- [x] **Initialize Repository and Virtual Environment:**
  - [ ] Create a new Git repository.
  - [ ] Set up a virtual environment.
- [x] **Folder Structure:**
  - [ ] Create `cli/` folder for the main CLI entry point.
  - [ ] Create `commands/` folder:
    - [ ] `create.py` (for the "sm create" command)
    - [ ] `run.py` (for the "sm run" command)
  - [ ] Create `integrations/` folder:
    - [ ] `github_integration.py` (handles GitHub Gist uploads/downloads and mapping sync)
    - [ ] `pydantic_ai_integration.py` (handles script generation and interactive refinement with PydanticAI)
  - [ ] Create `utils/` folder:
    - [ ] `mapping_manager.py` (manages the local JSON mapping file)
    - [ ] `logger.py` (centralized logging configuration)
  - [ ] Create `tests/` folder for unit and integration tests.
- [x] **Project Files:**
  - [ ] Create `requirements.txt` listing dependencies (e.g., `click`, `rich`, `uv`, `pydantic-ai`, `PyGithub`, etc.).
  - [ ] Create a `README.md` file with basic project information.

---

## CLI Foundation
- [x] **Main CLI Entry Point:**
  - [ ] Create `cli.py` using Click.
  - [ ] Define the main command group `sm`.
  - [ ] Add subcommands `create` and `run` with placeholder actions.
  - [ ] Verify that each subcommand prints a confirmation message when invoked.

---

## Mapping File Management
- [x] **Mapping Manager Module (`mapping_manager.py`):**
  - [ ] Implement a function to read the local mapping file (`~/.sm/mapping.json`).
  - [ ] Implement a function to write/update the mapping file.
  - [ ] Implement functions to add a new mapping entry and look up an entry by script name.
  - [ ] Ensure the module handles missing files by creating them as needed.
  - [ ] Add error handling and logging.

---

## GitHub Integration Module
- [ ] **GitHub Integration (`github_integration.py`):**
  - [ ] Implement authentication using the PAT from the `GITHUB_PAT` environment variable.
  - [ ] Create a function to upload a script (string content) as a GitHub Gist and return the Gist ID.
  - [ ] Create a function to download a script from a given Gist ID.
  - [ ] Create a function to sync the local mapping file with a remote Gist (commit and push changes).
  - [ ] Include robust error handling and logging.

---

## PydanticAI Integration Module
- [ ] **PydanticAI Integration (`pydantic_ai_integration.py`):**
  - [ ] Implement a function that accepts a prompt string and uses PydanticAI to generate a Python script.
  - [ ] Ensure the generated script includes inline metadata per uv’s default (PEP 723 compliant).
  - [ ] Support an interactive refinement loop: if preview mode is enabled, allow the user to request changes and regenerate the script until it’s accepted.
  - [ ] Return the final accepted script.

---

## SM Create Command Implementation
- [ ] **Create Command (`create.py`):**
  - [ ] Parse input arguments: script name and prompt, plus an optional `-p/--preview` flag.
  - [ ] Call the PydanticAI integration to generate the script.
  - [ ] If preview mode is enabled:
    - [ ] Display the generated script using Rich formatting.
    - [ ] Prompt the user: "Do you have any changes?" and, if yes, start an interactive refinement session with the PydanticAI LLM.
  - [ ] Once the script is accepted, upload it to GitHub Gist using the GitHub integration module.
  - [ ] Update the local mapping file with the script name, Gist ID, and a timestamp using the mapping manager.
  - [ ] Log all actions and errors.

---

## SM Run Command Implementation
- [ ] **Run Command (`run.py`):**
  - [ ] Parse input arguments: script name and any additional parameters (e.g., `prefix=gist`).
  - [ ] Look up the script in the local mapping file using the mapping manager.
  - [ ] Optionally, fetch the latest version from GitHub if required.
  - [ ] Execute the script using `uv run`, ensuring that inline metadata is processed.
  - [ ] Pass the command-line parameters to the script.
  - [ ] Capture and display the output, handling errors appropriately.
  - [ ] Log the execution process and any encountered issues.

---

## Logging, Error Handling, and Testing
- [ ] **Logging:**
  - [ ] Create a `logger.py` module in `utils/` to set up centralized logging.
  - [ ] Integrate logging across all modules.
- [ ] **Error Handling:**
  - [ ] Implement comprehensive error handling in each module (mapping, GitHub integration, PydanticAI integration, create and run commands).
  - [ ] Provide user-friendly error messages.
- [ ] **Testing:**
  - [ ] Write unit tests for `mapping_manager.py` functions.
  - [ ] Write unit tests for key functions in `github_integration.py`.
  - [ ] Write integration tests for the complete "sm create" and "sm run" flows.
  - [ ] Verify that all tests pass before final integration.

---

## Final Integration and Documentation
- [ ] **Wire CLI Commands:**
  - [ ] Update `cli.py` to import and attach the `create` and `run` command modules from the `commands/` folder.
  - [ ] Add help messages and usage instructions for each command.
- [ ] **Documentation:**
  - [ ] Update the README.md with installation steps, usage examples, and command descriptions.
  - [ ] Ensure inline comments and code documentation are clear and follow best practices.
- [ ] **Final Testing:**
  - [ ] Conduct end-to-end testing of both "sm create" and "sm run" workflows.
  - [ ] Validate that the mapping file syncs correctly with GitHub.
  - [ ] Confirm that interactive refinement works as expected in preview mode.

---

This comprehensive TODO checklist can be used as a step-by-step guide to track progress and ensure that every component is implemented and integrated correctly.
