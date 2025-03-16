"""Webdown: Convert web pages to markdown.

Webdown is a command-line tool and Python library for converting web pages to
clean, readable Markdown format. It supports various customization options
including table of contents generation, CSS selectors for extracting specific
content, and compact output formatting.

Basic usage:
    webdown https://example.com                # Output to stdout
    webdown https://example.com -o output.md   # Output to file
    webdown https://example.com -c -t          # Compact output with TOC

See the README.md file for more detailed usage instructions.
"""

__version__ = "0.4.0"
