"""Configuration classes for Webdown.

This module contains configuration classes used throughout the webdown package:
- WebdownConfig: Main configuration for HTML to Markdown conversion
- OutputFormat: Enum for supported output formats (Markdown, ClaudeXML)
- DocumentOptions: Configuration for output document structure

These classes centralize configuration options and provide defaults for
the conversion process, improving maintainability and API clarity.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


class OutputFormat(Enum):
    """Supported output formats for webdown.

    This enum defines the available output formats that webdown can produce.

    Attributes:
        MARKDOWN: Standard Markdown format
        CLAUDE_XML: Claude XML format optimized for Claude AI models
    """

    MARKDOWN = auto()
    CLAUDE_XML = auto()


@dataclass
class DocumentOptions:
    """Configuration for document output structure.

    This class contains settings that affect the structure of the generated document,
    independent of the output format.

    Attributes:
        include_toc (bool): Whether to generate a table of contents
        compact_output (bool): Whether to remove excessive blank lines
        body_width (int): Maximum line length for wrapping (0 for no wrapping)
        include_metadata (bool): Include metadata section with title, source URL, date
            (only applies to Claude XML format)
    """

    include_toc: bool = False
    compact_output: bool = False
    body_width: int = 0
    include_metadata: bool = True


@dataclass
class WebdownConfig:
    """Configuration options for HTML to Markdown conversion.

    This class centralizes all configuration options for the conversion process,
    focusing on the most useful options for LLM documentation processing.

    Attributes:
        url (Optional[str]): URL of the web page to convert
        include_links (bool): Whether to include hyperlinks (True) or plain text (False)
        include_images (bool): Whether to include images (True) or exclude them
        css_selector (Optional[str]): CSS selector to extract specific content
        show_progress (bool): Whether to display a progress bar during download
        format (OutputFormat): Output format (Markdown or Claude XML)
        document_options (DocumentOptions): Document structure configuration
    """

    # Source options
    url: Optional[str] = None
    show_progress: bool = False

    # Content options
    include_links: bool = True
    include_images: bool = True
    css_selector: Optional[str] = None

    # Output options
    format: OutputFormat = OutputFormat.MARKDOWN

    # We need to use field with default_factory to avoid mutable default value
    document_options: DocumentOptions = field(default_factory=DocumentOptions)


class WebdownError(Exception):
    """Exception for webdown errors.

    This exception class is used for all errors raised by the webdown package.
    The error type is indicated by a descriptive message and an error code,
    allowing programmatic error handling.

    Error types include:
        URL format errors: When the URL doesn't follow standard format
        Network errors: Connection issues, timeouts, HTTP errors
        Parsing errors: Issues with processing the HTML content
        Validation errors: Invalid parameters or configuration

    Attributes:
        code (str): Error code for programmatic error handling
    """

    def __init__(self, message: str, code: str = "UNEXPECTED_ERROR"):
        """Initialize a WebdownError.

        Args:
            message: Error message
            code: Error code for programmatic error handling
        """
        super().__init__(message)
        self.code = code
