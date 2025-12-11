# Webdown

[![Python Tests](https://github.com/kelp/webdown/actions/workflows/python-tests.yml/badge.svg)](https://github.com/kelp/webdown/actions/workflows/python-tests.yml)
[![codecov](https://codecov.io/gh/kelp/webdown/branch/main/graph/badge.svg)](https://codecov.io/gh/kelp/webdown)
[![PyPI version](https://badge.fury.io/py/webdown.svg)](https://badge.fury.io/py/webdown)
[![Python Versions](https://img.shields.io/pypi/pyversions/webdown.svg)](https://pypi.org/project/webdown/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python CLI tool for converting web pages to clean, readable Markdown format. Webdown makes it easy
to download documentation and feed it into an LLM coding tool.

## Why Webdown?

- **Clean Conversion**: Produces readable Markdown without formatting artifacts
- **Multi-Page Crawling**: Crawl entire documentation sites with `webdown crawl`
- **Selective Extraction**: Target specific page sections with CSS selectors
- **Claude XML Format**: Optimized output format for Anthropic's Claude AI models
- **Progress Tracking**: Visual download progress for large pages with `-p` flag
- **Optimized Handling**: Automatic streaming for large pages (>10MB) with no
  configuration required

## Use Cases

### Documentation for AI Coding Assistants

Webdown is particularly useful for preparing documentation to use with AI-assisted coding tools like Claude Code, GitHub Copilot, or ChatGPT:

- Convert technical documentation into clean Markdown for AI context
- Extract only the relevant parts of large documentation pages using CSS selectors
- Strip out images and formatting that might consume token context
- Generate well-structured tables of contents for better navigation

```bash
# Example: Convert API docs and store for AI coding context
webdown https://api.example.com/docs -s "main" -I -c -w 80 -o api_context.md
```

## Installation

### From PyPI

```bash
pip install webdown
```

### With Homebrew

```bash
# Add the tap
brew tap kelp/tools

# Install webdown
brew install webdown
```

### Install from Source

```bash
# Clone the repository
git clone https://github.com/kelp/webdown.git
cd webdown

# Install with pip
pip install .

# Or install with Poetry
poetry install
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
- `-p, --progress`: Show download progress bar (useful for large files)
- `--claude-xml`: Output in Claude XML format for use with Claude AI
- `--no-metadata`: Exclude metadata section from Claude XML output (metadata is included by default)
- `--no-date`: Exclude current date from metadata in Claude XML output (date is included by default)

For more details on the Claude XML format, see the [Anthropic documentation on Claude XML](https://docs.anthropic.com/claude/docs/advanced-data-extraction).

For large web pages (over 10MB), streaming mode is automatically used to optimize memory usage without any configuration required.

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

Generate Claude XML format for use with Claude AI:

```bash
webdown https://example.com --claude-xml -o doc.xml
```

Claude XML with no metadata section:

```bash
webdown https://example.com --claude-xml --no-metadata -o doc.xml
```

Claude XML without the current date in metadata:

```bash
webdown https://example.com --claude-xml --no-date -o doc.xml
```

## Crawling Multiple Pages

Crawl an entire documentation site:

```bash
webdown crawl https://docs.example.com/ -o ./output/
```

Crawl with depth and delay settings:

```bash
webdown crawl https://docs.example.com/ -o ./output/ --max-depth 5 --delay 2.0
```

Crawl from a sitemap:

```bash
webdown crawl --sitemap https://docs.example.com/sitemap.xml -o ./output/
```

Crawl with content options:

```bash
webdown crawl https://docs.example.com/ -o ./output/ -s "main" --claude-xml
```

### Crawl Options

- `--max-depth N`: Maximum crawl depth from seed URLs (default: 3)
- `--delay SECONDS`: Delay between requests (default: 1.0)
- `--same-domain`: Allow crawling any path on the same domain
- `--path-prefix PREFIX`: Only crawl URLs starting with this prefix
- `--sitemap URL`: Parse sitemap.xml instead of crawling links
- `--max-pages N`: Maximum number of pages to crawl (0 for unlimited)
- `-q, --quiet`: Suppress progress output

For complete documentation, use the `--help` flag:

```bash
webdown --help
```

## Documentation

API documentation is available online at [tcole.net/webdown](https://tcole.net/webdown/).

You can also generate the documentation locally with:

```bash
make docs        # Generate HTML docs in the docs/ directory
make docs-serve  # Start a local documentation server at http://localhost:8080
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

# Generate documentation
make docs

# Start documentation server
make docs-serve

# Publishing to PyPI (maintainers only)
# See CONTRIBUTING.md for details on the release process
make build         # Build package
make publish-test  # Publish to TestPyPI (for testing)

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
from webdown.converter import convert_url_to_markdown, WebdownConfig

# Basic conversion
markdown = convert_url_to_markdown("https://example.com")

# Using the Config object for more options
config = WebdownConfig(
    url="https://example.com",
    include_toc=True,
    css_selector="main",
    compact_output=True,
    body_width=80,
    show_progress=True
)
markdown = convert_url_to_markdown(config)

# Save to file
with open("output.md", "w") as f:
    f.write(markdown)

# Convert to Claude XML format (optimized for Anthropic's Claude AI)
from webdown.converter import convert_url_to_claude_xml, ClaudeXMLConfig

# Basic Claude XML conversion
xml = convert_url_to_claude_xml("https://example.com")

# With custom XML configuration
claude_config = ClaudeXMLConfig(
    include_metadata=True,   # Include title, URL, and date (default: True)
    add_date=True,           # Include current date in metadata (default: True)
    doc_tag="claude_documentation"  # Root document tag name (default)
)
xml = convert_url_to_claude_xml("https://example.com", claude_config)

# Save XML output
with open("output.xml", "w") as f:
    f.write(xml)

# For more information on Claude XML format, see:
# https://docs.anthropic.com/claude/docs/advanced-data-extraction
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests to make sure everything works:
   ```bash
   # Run standard tests
   poetry run pytest

   # Run tests with coverage
   poetry run pytest --cov=webdown

   # Run integration tests
   poetry run pytest --integration
   ```
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

Please make sure your code passes all tests, type checks, and follows our coding style (enforced by pre-commit hooks). We aim to maintain high code coverage (currently at 93%). When adding features, please include tests.

For more details, see [our Contributing Guide](https://tcole.net/webdown/contributing/).

## Support

If you encounter any problems or have feature requests, please [open an issue](https://github.com/kelp/webdown/issues) on GitHub.

## License

MIT License - see the [LICENSE](LICENSE) file for details.
