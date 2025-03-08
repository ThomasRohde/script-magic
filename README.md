# Script Magic 🪄

Command-line script utility toolkit that simplifies common scripting tasks!

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 🤖 **AI-Powered Script Generation**: Create Python scripts from natural language prompts using LiteLLM and Instructor, supporting:
  - OpenAI models
  - Anthropic Claude models
  - Google Gemini models

- ☁️ **GitHub Gist Integration**: Store and manage scripts in GitHub Gists for easy sharing and versioning.
- 🔄 **Simple Script Management**:  Run, update, edit, list, and delete your scripts with simple commands.
- 📦 **Automatic Dependency Management**: Script execution with `uv` handles dependencies automatically, based on PEP 723 metadata.
- 🚀 **Interactive Mode**: Refine generated scripts interactively before saving.
- 🖋️ **Built-in Code Editor**:  Edit scripts directly in your terminal with a Textual-based editor, featuring syntax highlighting and AI-powered editing capabilities.
- 🔄 **Cross-Device Synchronization**: Automatically sync your script inventory across devices using GitHub Gists.
- 🔎 **Smart Gist Detection**: Automatically finds your existing script mappings on GitHub.
- 🌐 **Multi-Environment Support**: Works seamlessly across different machines with the same GitHub account.
- 📝 **PEP 723 Metadata**:  Generated scripts include PEP 723 metadata for dependency and runtime information.
- ✨ **Enhanced Editing with AI**: Edit existing scripts using natural language instructions, powered by AI.
- 🎛️ **Configurable Models**: Choose different AI models for script generation and editing.


## Installation

Script Magic now uses `uv` for package management. Install `uv` first:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then, install Script Magic:

```bash
pip install script-magic
```
Or, for the latest version directly from GitHub:

```bash
uv pip install git+https://github.com/yourusername/script-magic.git
```
Replace `yourusername` with the actual username.

### Quick Install and Tool Install (Recommended)

```bash
# Clone the repository (Optional, but useful for development/contributing)
git clone https://github.com/yourusername/script-magic.git
cd script-magic

# Install with uv (ensures correct environment)
uv venv
uv pip install -e .

# Install as a tool using uv, forcing Python 3.13:
uv tool install --force --python 3.13 script-magic@latest

# Set up your environment variables
export OPENAI_API_KEY="your-openai-api-key" # Or your LiteLLM provider key
export MY_GITHUB_PAT="your-github-personal-access-token"

# Optional: Set up additional model provider keys if needed
export ANTHROPIC_API_KEY="your-anthropic-key"
export GOOGLE_API_KEY="your-gemini-key"
```
**Important:** The `uv tool install` command creates a separate, isolated environment for Script Magic. This helps avoid dependency conflicts.  You *must* use `uv run` to execute scripts that have dependencies installed via PEP 723.

## Usage

```bash
sm --help
```

### Creating Scripts

Generate a new script from a natural language prompt:

```bash
sm create hello-world "Create a script that prints 'Hello, World!' with a timestamp."
```

Generate with interactive preview:

```bash
sm create fibonacci --preview "Generate a script to print the first 10 Fibonacci numbers."
```

Specify a different AI model:

```bash
sm create list-files --model "anthropic/claude-3-opus" "List files in a directory."
```

### Running Scripts

Run a script that has been previously created:

```bash
sm run hello-world
```

Pass parameters to the script (Script Magic intelligently separates its own options from the script's arguments):

```bash
sm run hello-world --name="John"
```
Script Magic will automatically use `uv run` to execute the script in the correct environment, handling any dependencies.

Force refresh from GitHub before running:

```bash
sm run hello-world --refresh
```

Run a script in a new terminal window:

```bash
sm run visualize-data --in-terminal
```

The `--in-terminal` (`-t`) option runs the script in a new terminal window. This is useful for scripts with interactive elements or those producing visual output.

### Listing Scripts

View all scripts in your inventory:

```bash
sm list
```

Show detailed information:

```bash
sm list --verbose
```

Pull the latest scripts from GitHub before listing:

```bash
sm list --pull
```
Push local changes to Github before listing:
```bash
sm list --push
```

### Syncing Scripts

Push your local inventory and scripts to GitHub:

```bash
sm push
```

Pull the latest scripts and mapping from GitHub:

```bash
sm pull
```

### Deleting Scripts

Remove a script:

```bash
sm delete script-name
```

Force deletion without confirmation:

```bash
sm delete script-name --force
```

### Editing Scripts

Edit a script using the built-in Textual editor:

```bash
sm edit myscript
```

Use AI to modify the script during editing (Ctrl+P within the editor):

1.  Press Ctrl+P in the editor.
2.  Enter instructions like "Add a function to calculate the average."
3.  The AI will modify the script based on your instructions.

Specify a different model for AI-assisted editing:

```bash
sm edit myscript --model "anthropic/claude-3-opus"
```

## GitHub Integration

Script Magic automatically handles GitHub synchronization:

-   **First-time users**: Creates a new private Gist to store your script inventory.
-   **Existing users**: Finds your existing script inventory Gists automatically.
-   **Multiple devices**: Detects existing mappings and asks which version to keep.

## Configuration

Script Magic stores configuration in the `~/.sm` directory:

-   `~/.sm/mapping.json`: Maps script names to GitHub Gist IDs.
-   `~/.sm/gist_id.txt`: Stores the ID of the Gist containing your mapping file.
-   `~/.sm/logs/`: Log files for debugging.
-   `~/.sm/scripts/`: Local copies of your scripts.

## Structure

```
script-magic/
├── src/
│   └── script_magic/
│       ├── __init__.py                # CLI entry point & command registration.
│       ├── ai_integration.py          # AI script generation and editing.
│       ├── create.py                  # `create` command implementation.
│       ├── delete.py                  # `delete` command implementation.
│       ├── edit.py                    # `edit` command implementation (Textual TUI).
│       ├── github_gist_finder.py      # Finds existing mapping Gists.
│       ├── github_integration.py      # GitHub Gist API interaction.
│       ├── list.py                    # `list` command implementation.
│       ├── logger.py                  # Logging setup.
│       ├── mapping_manager.py         # Manages the script mapping (local & GitHub).
│       ├── mapping_setup.py           # Initializes mapping with GitHub sync.
│       ├── pep723.py                  # PEP 723 metadata parsing and updating.
│       ├── rich_output.py             # Rich-based console output utilities.
│       └── run.py                     # `run` command implementation.
├── README.md
└── ...
```

## Environment Variables

-   `OPENAI_API_KEY`: Your OpenAI API key (or key for your chosen LiteLLM provider).
-   `MY_GITHUB_PAT`: GitHub Personal Access Token with `gist` scope.

## Contributing

Contributions are welcome!  Please submit a Pull Request.

1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/amazing-feature`).
3.  Commit your changes (`git commit -m 'Add some amazing feature'`).
4.  Push to the branch (`git push origin feature/amazing-feature`).
5.  Open a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

-   [Instructor](https://github.com/jxnl/instructor)
-   [LiteLLM](https://github.com/BerriAI/litellm)
-   [Click](https://click.palletsprojects.com/)
-   [PyGitHub](https://github.com/PyGithub/PyGithub)
-   [Rich](https://github.com/Textualize/rich)
-   [Textual](https://github.com/Textualize/textual)
-   [uv](https://github.com/astral-sh/uv)

## Development

To install development dependencies:

```bash
uv pip install -e '.[dev,syntax]'
```
