"""Webdown: Convert web pages to markdown.

Webdown is a command-line tool and Python library for converting web pages to
clean, readable Markdown format. It provides a comprehensive set of options
for customizing the conversion process.

## Key Features

- Convert web pages to clean, readable Markdown or Claude XML
- Extract specific content using CSS selectors
- Generate table of contents from headings
- Control link and image handling
- Customize document formatting
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
from webdown import convert_url
markdown = convert_url("https://example.com")

# Using the configuration object with Markdown output
from webdown import WebdownConfig, DocumentOptions, convert_url
doc_options = DocumentOptions(include_toc=True, body_width=80)
config = WebdownConfig(
    url="https://example.com",
    css_selector="main",
    document_options=doc_options
)
markdown = convert_url(config)

# Convert to Claude XML format
from webdown import WebdownConfig, OutputFormat, convert_url
config = WebdownConfig(
    url="https://example.com",
    format=OutputFormat.CLAUDE_XML
)
xml_content = convert_url(config)
```

See the API documentation for detailed descriptions of all options.
"""

__version__ = "0.5.0"

# Import CLI module
from webdown import cli

# Import key classes and functions for easy access
from webdown.config import DocumentOptions, OutputFormat, WebdownConfig, WebdownError
from webdown.converter import convert_url_to_claude_xml  # For backward compatibility
from webdown.converter import convert_url_to_markdown  # For backward compatibility
from webdown.converter import convert_url, html_to_markdown
from webdown.error_utils import ErrorCode
from webdown.html_parser import fetch_url
from webdown.validation import validate_css_selector, validate_url

# Define public API
__all__ = [
    "WebdownConfig",
    "DocumentOptions",
    "OutputFormat",
    "WebdownError",
    "convert_url",
    "convert_url_to_markdown",  # For backward compatibility
    "convert_url_to_claude_xml",  # For backward compatibility
    "fetch_url",
    "html_to_markdown",
    "validate_url",
    "validate_css_selector",
    "ErrorCode",
    "cli",
]
