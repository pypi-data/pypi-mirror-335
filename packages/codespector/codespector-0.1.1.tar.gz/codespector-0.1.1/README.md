# CodeSpector

CodeSpector is a Python package designed to review code changes for quality and security issues using AI chat agents. It supports different chat agents like Codestral and ChatGPT.

## Features

- Automated code review using AI chat agents.
- Supports multiple chat agents and models.
- Generates detailed review reports in markdown format.
- Configurable via environment variables and command-line options.

## Installation

To install the package, use the following command:

```sh
pip install codespector
```

```sh
uv add codespector
```

## Usage

### Command-Line Interface

You can use the `codespector` command to start a code review. Below are the available options:

```sh
Usage: codespector [OPTIONS]

Options:
  --system-content TEXT       Content which used in system field for agent
                              [default: Ты код ревьювер. Отвечай на русском языке.]
  --output-dir TEXT           Select the output directory [default: codespector]
  -b, --compare-branch TEXT   Select the branch to compare the current one with
                              [default: develop]
  --chat-agent [codestral|chatgpt]
                              Choose the chat agent to use [default: codestral]
  --chat-model TEXT           Choose the chat model to use
  --chat-token TEXT           Chat agent token
  --mode [local]              Choose the mode of the application [default: local]
  --version                   Show the version and exit.
  --help                      Show this message and exit.
```

### Example

To run a code review, use the following command:

```sh
codespector --chat-token YOUR_CHAT_TOKEN --chat-agent codestral --compare-branch develop
```

## Configuration

You can also configure CodeSpector using environment variables. Create a `.env` file in the root directory of your project with the following content:

```
CODESPECTOR_SYSTEM_CONTENT=Ты код ревьювер. Отвечай на русском языке.
CODESPECTOR_OUTPUT_DIR=codespector
CODESPECTOR_CHAT_AGENT=codestral
CODESPECTOR_CHAT_MODEL=codestral-latest
CODESPECTOR_CHAT_TOKEN=YOUR_CHAT_TOKEN
```

## Makefile Commands

- `lint`: Run linting and formatting checks.
- `format`: Format the code.
- `fix`: Fix linting issues and format the code.
- `test`: Run the tests.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.