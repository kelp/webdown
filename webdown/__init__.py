"""Webdown: Convert web pages and HTML files to markdown.

Webdown is a command-line tool and Python library for converting web pages and
local HTML files to clean, readable Markdown format. It provides a comprehensive
set of options for customizing the conversion process.

## Key Features

- Convert web pages and local HTML files to clean, readable Markdown or Claude XML
- Extract specific content using CSS selectors
- Generate table of contents from headings
- Control link and image handling
- Customize document formatting
- Show progress bar for large downloads
- Configure text wrapping and line breaks

## Command-line Usage

Webdown provides a CLI for easy conversion of web pages or HTML files to Markdown.

```bash
# Convert web pages
webdown -u https://example.com                # Output to stdout
webdown -u https://example.com -o output.md   # Output to file
webdown -u https://example.com -c -t          # Compact output with TOC

# Convert local HTML files
webdown -f page.html                     # Output to stdout
webdown -f page.html -o output.md        # Output to file
webdown -f page.html -s "main" -t        # Extract content with TOC

# Advanced options (work with both URLs and files)
webdown -u https://example.com -s "main" -I -c -w 80 -o output.md
webdown -f page.html -s "main" -I -c -w 80 -o output.md
```

**For detailed CLI documentation and all available options,**
**see the [CLI module](./webdown/cli.html).**

## Library Usage

```python
# Convert a URL to Markdown
from webdown import convert_url, WebdownConfig, OutputFormat
config = WebdownConfig(url="https://example.com", format=OutputFormat.MARKDOWN)
markdown = convert_url(config)

# Convert a local HTML file to Markdown
from webdown import convert_file, WebdownConfig, OutputFormat
config = WebdownConfig(file_path="page.html", format=OutputFormat.MARKDOWN)
markdown = convert_file(config)

# Using the configuration object with additional options
from webdown import WebdownConfig, DocumentOptions, OutputFormat, convert_url
doc_options = DocumentOptions(include_toc=True, body_width=80)
config = WebdownConfig(
    url="https://example.com",
    css_selector="main",
    format=OutputFormat.MARKDOWN,
    document_options=doc_options
)
markdown = convert_url(config)

# Convert to Claude XML format (works for both URLs and local files)
from webdown import WebdownConfig, OutputFormat, convert_url, convert_file
config = WebdownConfig(
    url="https://example.com",
    format=OutputFormat.CLAUDE_XML
)
xml_content = convert_url(config)
```

See the API documentation for detailed descriptions of all options.
"""

__version__ = "0.7.0"

# Import CLI module
from webdown import cli

# Import key classes and functions for easy access
from webdown.config import DocumentOptions, OutputFormat, WebdownConfig, WebdownError
from webdown.converter import convert_file, convert_url, html_to_markdown
from webdown.error_utils import ErrorCode
from webdown.html_parser import fetch_url, read_html_file
from webdown.validation import validate_css_selector, validate_url

# Define public API
__all__ = [
    "WebdownConfig",
    "DocumentOptions",
    "OutputFormat",
    "WebdownError",
    "convert_url",
    "convert_file",
    "fetch_url",
    "read_html_file",
    "html_to_markdown",
    "validate_url",
    "validate_css_selector",
    "ErrorCode",
    "cli",
]
