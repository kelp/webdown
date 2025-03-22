"""Configuration classes for Webdown.

This module contains configuration classes used throughout the webdown package:
- WebdownConfig: Main configuration for HTML to Markdown conversion
- ClaudeXMLConfig: Configuration for Claude XML output format

These classes centralize configuration options and provide defaults for
the conversion process, improving maintainability and API clarity.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ClaudeXMLConfig:
    """Configuration options for Claude XML output format.

    This class contains settings specific to the Claude XML output format,
    providing options to customize the structure and metadata of the generated document.

    Attributes:
        include_metadata (bool): Include metadata section with title, source URL, date
        add_date (bool): Include current date in the metadata section
        doc_tag (str): Root document tag name
        beautify (bool): Add indentation and newlines for human readability
    """

    include_metadata: bool = True
    add_date: bool = True
    doc_tag: str = "claude_documentation"
    beautify: bool = True


@dataclass
class WebdownConfig:
    """Configuration options for HTML to Markdown conversion.

    This class centralizes all configuration options for the conversion process,
    focusing on the most useful options for LLM documentation processing.

    Attributes:
        url (Optional[str]): URL of the web page to convert
        include_links (bool): Whether to include hyperlinks (True) or plain text (False)
        include_images (bool): Whether to include images (True) or exclude them
        include_toc (bool): Whether to generate table of contents
        css_selector (Optional[str]): CSS selector to extract specific content
        compact_output (bool): Whether to remove excessive blank lines
        body_width (int): Maximum line length for wrapping (0 for no wrapping)
        show_progress (bool): Whether to display a progress bar during download
    """

    # Core options
    url: Optional[str] = None
    include_links: bool = True
    include_images: bool = True
    include_toc: bool = False
    css_selector: Optional[str] = None
    compact_output: bool = False
    body_width: int = 0
    show_progress: bool = False


class WebdownError(Exception):
    """Exception for webdown errors.

    This exception class is used for all errors raised by the webdown package.
    The error type is indicated by a descriptive message and can be
    distinguished by checking the message content.

    Error types include:
        URL format errors: When the URL doesn't follow standard format
        Network errors: Connection issues, timeouts, HTTP errors
        Parsing errors: Issues with processing the HTML content
    """

    pass
