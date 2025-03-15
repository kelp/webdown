# Webdown

A Python CLI tool for converting web pages to Markdown.

## Installation

```bash
pip install webdown
```

## Usage

Basic usage:

```bash
webdown https://example.com/page.html -o output.md
```

Output to stdout:

```bash
webdown https://example.com/page.html
```

### Options

- `-o, --output`: Output file (default: stdout)
- `-t, --toc`: Generate table of contents
- `-L, --no-links`: Strip hyperlinks
- `-I, --no-images`: Exclude images
- `-c, --css SELECTOR`: CSS selector to extract specific content

## Examples

Generate markdown with a table of contents:

```bash
webdown https://example.com -t -o output.md
```

Extract only main content:

```bash
webdown https://example.com -c "main" -o output.md
```

Strip links and images:

```bash
webdown https://example.com -L -I -o output.md
```

## Development

### Prerequisites

- Python 3.10+ (3.13 recommended)
- [Poetry](https://python-poetry.org/docs/#installation) for dependency management

### Setup

```bash
# Clone the repository
git clone https://github.com/username/webdown.git
cd webdown

# Install dependencies with Poetry
poetry install
poetry run pre-commit install

# Optional: Start a Poetry shell for interactive development
poetry shell
```

### Development Commands

We use a Makefile to streamline development tasks:

```bash
# Install dependencies
make install

# Run tests
make test

# Run tests with coverage
make test-coverage

# Run integration tests
make integration-test

# Run linting
make lint

# Run type checking
make type-check

# Format code
make format

# Run all pre-commit hooks
make pre-commit

# Run all checks (lint, type-check, test)
make all-checks

# Build package
make build

# Start interactive Poetry shell
make shell

# Show all available commands
make help
```

### Poetry Commands

You can also use Poetry directly:

```bash
# Start an interactive shell in the Poetry environment
poetry shell

# Run a command in the Poetry environment
poetry run pytest

# Add a new dependency
poetry add requests

# Add a development dependency
poetry add --group dev black

# Update dependencies
poetry update

# Build package
poetry build
```

## License

MIT
