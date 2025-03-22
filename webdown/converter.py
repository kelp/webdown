"""HTML to Markdown and Claude XML conversion functionality.

This module serves as the main entry point for the webdown package, providing
the primary functions for converting web content to Markdown and Claude XML formats.

The conversion process involves multiple steps:
1. Fetch and validate web content
2. Convert HTML to Markdown
3. Optionally convert Markdown to Claude XML format

Key functions:
- convert_url_to_markdown: Fetch a URL and convert to Markdown
- convert_url_to_claude_xml: Fetch a URL and convert to Claude XML
"""

from typing import Optional

from webdown.config import ClaudeXMLConfig, WebdownConfig, WebdownError
from webdown.html_parser import (
    _check_streaming_needed,
    fetch_url,
    validate_css_selector,
    validate_url,
)
from webdown.markdown_converter import html_to_markdown
from webdown.xml_converter import markdown_to_claude_xml

__all__ = [
    "WebdownConfig",
    "ClaudeXMLConfig",
    "WebdownError",
    "validate_url",
    "validate_css_selector",
    "fetch_url",
    "html_to_markdown",
    "markdown_to_claude_xml",
    "convert_url_to_markdown",
    "convert_url_to_claude_xml",
]


def _get_normalized_config(url_or_config: str | WebdownConfig) -> WebdownConfig:
    """Get a normalized WebdownConfig object with validated URL.

    This function centralizes URL validation logic for the entire converter module.
    All code paths that need a validated URL should go through this function.

    Args:
        url_or_config: URL string or WebdownConfig object

    Returns:
        Normalized WebdownConfig with validated URL

    Raises:
        WebdownError: If URL is invalid or missing
    """
    # Create config object if a URL string was provided
    if isinstance(url_or_config, str):
        config = WebdownConfig(url=url_or_config)
    else:
        config = url_or_config
        if config.url is None:
            raise WebdownError("URL must be provided in the config object")

    # At this point config.url cannot be None due to the check above
    url = config.url
    assert url is not None

    # Validate URL format - centralized validation for the entire module
    if not validate_url(url):
        raise WebdownError(f"Invalid URL format: {url}")

    return config


def convert_url_to_markdown(url_or_config: str | WebdownConfig) -> str:
    """Convert a web page to markdown.

    This function accepts either a URL string or a WebdownConfig object.
    If a URL string is provided, it will be used to create a WebdownConfig object.

    For large web pages (over 10MB), streaming mode is automatically used.

    Args:
        url_or_config: URL of the web page or a WebdownConfig object

    Returns:
        Markdown content

    Raises:
        WebdownError: If URL is invalid or cannot be fetched

    Examples:
        # Using URL string
        markdown = convert_url_to_markdown("https://example.com")

        # Using config object
        config = WebdownConfig(
            url="https://example.com",
            include_toc=True,
            show_progress=True
        )
        markdown = convert_url_to_markdown(config)
    """
    # Get normalized config with validated URL
    config = _get_normalized_config(url_or_config)
    # At this point, the URL has been validated and cannot be None
    url = config.url
    assert url is not None

    try:
        # Check if streaming is needed based on content size
        # This is mainly for compatibility with tests that expect this behavior
        _check_streaming_needed(url)

        # Fetch the HTML content (URL already validated by _get_normalized_config)
        html = fetch_url(url, show_progress=config.show_progress)

        # Convert HTML to Markdown
        return html_to_markdown(html, config)

    except Exception as e:
        # This is a fallback for any other request exceptions
        raise WebdownError(f"Error fetching {url}: {str(e)}")


def convert_url_to_claude_xml(
    url_or_config: str | WebdownConfig,
    claude_xml_config: Optional[ClaudeXMLConfig] = None,
) -> str:
    """Convert a web page directly to Claude XML format.

    This function fetches a web page and converts it to Claude XML format,
    optimized for use with Claude AI models.

    Args:
        url_or_config: URL to fetch or WebdownConfig object
        claude_xml_config: XML output configuration

    Returns:
        Claude XML formatted content

    Raises:
        WebdownError: If URL is invalid or cannot be fetched
    """
    # Determine source URL for metadata
    source_url = url_or_config if isinstance(url_or_config, str) else url_or_config.url

    # Use the existing markdown conversion pipeline - keep the original parameter type
    # for backward compatibility with tests
    markdown = convert_url_to_markdown(url_or_config)

    # Convert the markdown to Claude XML
    return markdown_to_claude_xml(markdown, source_url, claude_xml_config)
