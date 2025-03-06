# Script Magic 🪄

Command-line script utility toolkit that simplifies common scripting tasks!

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 🤖 **AI-Powered Script Generation**: Create Python scripts from natural language prompts using OpenAI's GPT models
- ☁️ **GitHub Gist Integration**: Store and manage scripts in GitHub Gists for easy sharing and versioning
- 🔄 **Simple Script Management**: Run, update, and manage your scripts with easy commands
- 📦 **Automatic Dependency Management**: Script execution with `uv` handles dependencies automatically
- 🚀 **Interactive Mode**: Refine generated scripts interactively before saving
- 🔄 **Cross-Device Synchronization**: Automatically find and sync your script inventory across devices using GitHub Gists
- 🔎 **Smart Gist Detection**: Automatically finds your existing script mappings on GitHub
- 🌐 **Multi-Environment Support**: Works seamlessly across different machines with the same GitHub account
- 🖋️ **Syntax Highlighting**: Built-in code editor with syntax highlighting (requires optional dependencies)

## Installation

```bash
pip install script-magic
```

### Prerequisites

- Python 3.9+
- [uv](https://github.com/astral-sh/uv) for Python package management and script execution
- GitHub account with a Personal Access Token
- OpenAI API key

### Quick Install

```bash
# Clone the repository
git clone https://github.com/yourusername/script-magic.git
cd script-magic

# Install with uv
uv venv
uv pip install -e .

# Set up your environment variables
export OPENAI_API_KEY="your-openai-api-key"
export MY_GITHUB_PAT="your-github-personal-access-token"
```

### Optional Dependencies

For enhanced features such as syntax highlighting in the editor:

```bash
pip install 'script-magic[syntax]'
```

## Usage

```python
# Import the library
from script_magic import some_function

# Use the command-line tool
sm --help
```

### Creating Scripts

Generate a new script from a natural language prompt:

```bash
sm create hello-world "Create a script that prints 'Hello, World!' with timestamp"
```

Generate with interactive preview:

```bash
sm create fibonacci --preview "Generate a script to print the first 10 Fibonacci numbers"
```

### Running Scripts

Run a script that has been previously created:

```bash
sm run hello-world
```

Pass parameters to the script:

```bash
sm run hello-world --name="John"
```

Force refresh from GitHub before running:

```bash
sm run hello-world --refresh
```

Run a script in a new terminal window:

```bash
sm run visualize-data --in-terminal
```

The `--in-terminal` (`-t`) option will run the script in a new terminal window that remains open until closed by the user.
This is particularly useful for scripts with interactive elements or those that produce visual output.

### Listing Scripts

View all scripts in your inventory:

```bash
sm list
```

Show detailed information about your scripts:

```bash
sm list --verbose
```

Pull the latest scripts from GitHub before listing:

```bash
sm list --pull
```

Push your local script inventory to GitHub while listing:

```bash
sm list --push
```

### Syncing Scripts

Sync your local inventory to GitHub:

```bash
sm sync
```

Pull the latest mapping from GitHub:

```bash
sm pull
```

### Deleting Scripts

Remove a script from both local inventory and GitHub Gists:

```bash
sm delete script-name
```

Force deletion without confirmation:

```bash
sm delete script-name --force
```

### Editing Scripts

Edit a script with syntax highlighting (if dependencies are installed):

```bash
script-magic edit myscript
```

## GitHub Integration

Script Magic automatically handles GitHub synchronization:

- First-time users: Script Magic creates a new private Gist to store your script inventory
- Existing users: Script Magic finds your existing script inventory Gists automatically
- Multiple devices: Script Magic detects existing mappings and asks which version to keep

## Configuration

Script Magic stores configuration in the `~/.sm` directory:

- `~/.sm/mapping.json`: Maps script names to GitHub Gist IDs
- `~/.sm/gist_id.txt`: Stores the ID of the GitHub Gist containing your mapping file
- `~/.sm/logs/`: Log files for debugging

## Structure

```
script-magic/
├── src/
│   └── script_magic/
│       ├── __init__.py                # CLI entry point with command registration
│       ├── create.py                  # Script creation command
│       ├── run.py                     # Script execution command
│       ├── list.py                    # Script listing command
│       ├── delete.py                  # Script deletion command
│       ├── github_integration.py      # GitHub Gist API integration
│       ├── github_gist_finder.py      # Finds existing mapping Gists
│       ├── pydantic_ai_integration.py # AI script generation
│       ├── mapping_manager.py         # Script mapping management
│       ├── mapping_setup.py           # Initializes mapping with GitHub sync
│       ├── logger.py                  # Logging configuration
│       └── rich_output.py             # Terminal output formatting
```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `MY_GITHUB_PAT`: GitHub Personal Access Token with Gist permissions

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [PydanticAI](https://ai.pydantic.dev/) for AI integration
- [Click](https://click.palletsprojects.com/) for the CLI interface
- [PyGitHub](https://github.com/PyGithub/PyGithub) for GitHub API integration
- [Rich](https://github.com/Textualize/rich) for beautiful terminal output

## Development 

To install development dependencies:

```bash
pip install -e '.[dev,syntax]'
```
