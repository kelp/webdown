"""Webdown: Convert web pages to markdown.

Webdown is a command-line tool and Python library for converting web pages to
clean, readable Markdown format. It provides a comprehensive set of options
for customizing the conversion process.

## Key Features

- Convert web pages to clean, readable Markdown
- Extract specific content using CSS selectors
- Generate table of contents from headings
- Control link and image handling
- Customize Markdown formatting style
- Show progress bar for large downloads
- Configure text wrapping and line breaks

## Command-line Usage

Webdown provides a command-line interface for easy conversion of web pages to Markdown.

```bash
# Basic usage
webdown https://example.com                # Output to stdout
webdown https://example.com -o output.md   # Output to file
webdown https://example.com -c -t          # Compact output with TOC

# Advanced options
webdown https://example.com -s "main" -I -c -w 80 -o output.md
```

**For detailed CLI documentation and all available options,**
**see the [CLI module](./webdown/cli.html).**

## Library Usage

```python
# Simple conversion
from webdown import convert_url_to_markdown
markdown = convert_url_to_markdown("https://example.com")

# Using the configuration object
from webdown import WebdownConfig, convert_url_to_markdown
config = WebdownConfig(
    url="https://example.com",
    include_toc=True,
    css_selector="main",
    body_width=80
)
markdown = convert_url_to_markdown(config)
```

See the API documentation for detailed descriptions of all options.
"""

__version__ = "0.5.0"

# Import CLI module
from webdown import cli

# Import key classes and functions for easy access
from webdown.converter import (
    WebdownConfig,
    WebdownError,
    convert_url_to_markdown,
    fetch_url,
    html_to_markdown,
)

# Define public API
__all__ = [
    "WebdownConfig",
    "WebdownError",
    "convert_url_to_markdown",
    "fetch_url",
    "html_to_markdown",
    "cli",
]
