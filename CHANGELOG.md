# Changelog

All notable changes to Script Magic will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- VS Code settings for Copilot instructions

### Changed
- Updated .gitignore file

## [1.7.1] - 2025-03-08
### Changed
- Increased max_tokens in AnthropicProvider
### Removed
- Unused test file

## [1.7.0] - 2025-03-08
### Added
- Local script file deletion in delete_script function
### Changed
- Patched requests to disable SSL verification and suppress warnings in GitHub integration
- Added noqa comments to suppress linting warnings in ScriptEditor class

## [1.6.0] - 2025-03-08
### Changed
- Updated dependencies
- Enhanced README for AI model support

## [1.5.0] - 2025-03-08
### Added
- pip-system-certs dependency

## [1.4.0] - 2025-03-07
### Changed
- Updated dependencies in pyproject.toml and uv.lock for instructor package

## [1.3.0] - 2025-03-07
### Added
- LoadingIndicator for progress modal

### Changed
- Updated README.md to enhance feature descriptions, installation instructions, and usage examples
- Refactored progress modal to use LoadingIndicator
- Updated loading animation documentation

### Removed
- Loading and progress documentation files

## [1.2.0] - 2025-03-06
### Added
- Progress bar functionality

### Changed
- Refactored AI integration
- Adjusted progress modal width

## [1.1.5] - 2025-03-06
### Changed
- Minor version updates

## [1.1.4] - 2025-03-06
### Added
- Model support for script creation/editing

### Changed
- Updated dependencies
- Refactored imports to use ai_integration module

### Removed
- Terminal input handling module
- Unused thread_utils.py file

## [1.1.1] - 2025-03-04
### Reverted
- Model selection for script creation and editing defaulting to "openai:gpt-4o-mini"

## [1.1.0] - 2025-03-03
### Added
- Terminal input handling utilities
- PEP 723 metadata parsing and correction functionality
- Setup.py for improved project structure

### Changed
- Updated .gitignore and pyproject.toml for improved dependency management
- Enhanced notification management in ScriptEditor
- Refactored terminal command execution for improved cross-platform compatibility

## [1.0.0] - 2025-03-02
### Added
- Support for running scripts in a new terminal window with interactive output
- Script generation with description and tags
- Tag extraction functionality

### Changed
- Updated GITHUB PAT environment variable

## [0.1.0] - 2025-03-01
### Added
- GitHub Gist integration for mapping management
- 'Delete' command for removing scripts
- 'List' command with filtering options
- 'Run' command for executing scripts from GitHub Gists
- Pull/push functionality for GitHub mapping synchronization
- UTF-8 encoding for file operations and subprocess execution
- Rich table formatting for script listing
- Dynamic console log level configuration
- README documentation with features, installation, and usage instructions
- CLI commands for script creation and execution
- Core functionalities for commands and utilities
- Initial project structure with Python version and dependencies

### Changed
- Renamed _sync_from_github to pull_mapping
- Renamed sync_mapping to push_mapping
- Refactored CLI structure by consolidating command registrations
- Refactored project structure by consolidating modules

