# Webdown

[![Python Tests](https://github.com/kelp/webdown/actions/workflows/python-tests.yml/badge.svg)](https://github.com/kelp/webdown/actions/workflows/python-tests.yml)
[![codecov](https://codecov.io/gh/kelp/webdown/branch/main/graph/badge.svg)](https://codecov.io/gh/kelp/webdown)
[![PyPI version](https://badge.fury.io/py/webdown.svg)](https://badge.fury.io/py/webdown)
[![Python Versions](https://img.shields.io/pypi/pyversions/webdown.svg)](https://pypi.org/project/webdown/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python CLI tool for converting web pages to clean, readable Markdown format. Webdown makes it easy to extract content from websites for documentation, notes, content migration, or offline reading.

## Why Webdown?

- **Clean Conversion**: Produces readable Markdown without formatting artifacts
- **Selective Extraction**: Target specific page sections with CSS selectors
- **Customization Options**: Control links, images, text wrapping, and more
- **Progress Tracking**: Visual download progress for large pages
- **Python Integration**: Use as a CLI tool or integrate into your Python projects

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
- `-s, --css SELECTOR`: CSS selector to extract specific content
- `-c, --compact`: Remove excessive blank lines from the output
- `-w, --width N`: Set the line width for wrapped text (0 for no wrapping)
- `-p, --progress`: Show download progress bar

## Examples

Generate markdown with a table of contents:

```bash
webdown https://example.com -t -o output.md
```

Extract only main content:

```bash
webdown https://example.com -s "main" -o output.md
```

Strip links and images:

```bash
webdown https://example.com -L -I -o output.md
```

Compact output with progress bar and line wrapping:

```bash
webdown https://example.com -c -p -w 80 -o output.md
```

For complete documentation, use the `--help` flag:

```bash
webdown --help
```

## Development

### Prerequisites

- Python 3.10+ (3.13 recommended)
- [Poetry](https://python-poetry.org/docs/#installation) for dependency management

### Setup

```bash
# Clone the repository
git clone https://github.com/kelp/webdown.git
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

## Python API Usage

Webdown can also be used as a Python library in your own projects:

```python
from webdown.converter import convert_url_to_markdown

# Basic conversion
markdown = convert_url_to_markdown("https://example.com")

# With all options
markdown = convert_url_to_markdown(
    url="https://example.com",
    include_links=True,
    include_images=True,
    include_toc=True,
    css_selector="main",  # Only extract main content
    compact_output=True,  # Remove excessive blank lines
    body_width=80,        # Wrap text at 80 characters
    show_progress=True    # Show download progress bar
)

# Save to file
with open("output.md", "w") as f:
    f.write(markdown)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests to make sure everything works (`poetry run pytest`)
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

Please make sure your code passes all tests, type checks, and follows our coding style (enforced by pre-commit hooks).

For more details, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Support

If you encounter any problems or have feature requests, please [open an issue](https://github.com/kelp/webdown/issues) on GitHub.

## License

MIT License - see the [LICENSE](LICENSE) file for details.
