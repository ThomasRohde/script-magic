# Script Magic 🪄

Script Magic is a CLI tool for creating, managing, and running Python scripts with GitHub Gists integration and AI-powered script generation.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 🤖 **AI-Powered Script Generation**: Create Python scripts from natural language prompts using OpenAI's GPT models
- ☁️ **GitHub Gist Integration**: Store and manage scripts in GitHub Gists for easy sharing and versioning
- 🔄 **Simple Script Management**: Run, update, and manage your scripts with easy commands
- 📦 **Automatic Dependency Management**: Script execution with `uv` handles dependencies automatically
- 🚀 **Interactive Mode**: Refine generated scripts interactively before saving

## Installation

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
export GITHUB_PAT="your-github-personal-access-token"
```

## Usage

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

## Configuration

Script Magic stores configuration in the `~/.sm` directory:

- `~/.sm/config.json`: Main configuration file
- `~/.sm/scripts/`: Local cache of downloaded scripts
- `~/.sm/mapping.json`: Maps script names to GitHub Gist IDs

## Structure

```
script-magic/
├── cli.py                     # Main CLI entry point
├── commands/                  # Command implementations
│   ├── create.py              # Script creation command
│   └── run.py                 # Script execution command
├── integrations/              # External service integrations
│   ├── github_integration.py  # GitHub Gist API integration
│   └── pydantic_ai_integration.py  # AI script generation
└── utils/                     # Utility modules
    ├── logger.py              # Logging configuration
    ├── mapping_manager.py     # Script mapping management
    └── rich_output.py         # Terminal output formatting
```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `GITHUB_PAT`: GitHub Personal Access Token with Gist permissions
- `SM_CONFIG_DIR`: (Optional) Custom directory for Script Magic configuration

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
