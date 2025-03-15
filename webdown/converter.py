"""HTML to Markdown conversion functionality.

This module provides functions for fetching web content and converting it to Markdown.
Key features include:
- URL validation and HTML fetching with proper error handling
- HTML to Markdown conversion using html2text
- Support for content filtering with CSS selectors
- Table of contents generation
- Removal of excessive blank lines (compact mode)
- Removal of zero-width spaces and other invisible characters

The main entry point is the `convert_url_to_markdown` function, which handles
the entire process from fetching a URL to producing clean Markdown output.
"""

from typing import Optional
from urllib.parse import urlparse

import html2text
import requests
from bs4 import BeautifulSoup


class WebdownError(Exception):
    """Base exception for webdown errors.

    This is the parent class for all custom exceptions raised by the webdown package.
    It inherits from the standard Exception class and serves as a way to catch
    all webdown-specific errors.
    """

    pass


class NetworkError(WebdownError):
    """Exception raised for network-related errors.

    This exception is raised when there are problems with the network connection
    or HTTP request, such as timeouts, connection errors, or HTTP error status codes.

    Examples:
        - Connection timeout
        - DNS resolution failure
        - Server returned 404, 500, etc.
        - SSL certificate errors
    """

    pass


class InvalidURLError(WebdownError):
    """Exception raised for invalid URL format.

    This exception is raised when the provided URL is not properly formatted
    according to URL standards (scheme://netloc/path?query#fragment).

    Examples:
        - Missing scheme (http://, https://)
        - Missing domain
        - Malformed URL structure
    """

    pass


def validate_url(url: str) -> bool:
    """Validate URL format.

    Args:
        url: URL to validate

    Returns:
        True if valid, False otherwise

    >>> validate_url('https://example.com')
    True
    >>> validate_url('not_a_url')
    False
    """
    parsed = urlparse(url)
    return bool(parsed.scheme and parsed.netloc)


def fetch_url(url: str) -> str:
    """Fetch HTML content from URL.

    Args:
        url: URL to fetch

    Returns:
        HTML content as string

    Raises:
        InvalidURLError: If URL format is invalid
        NetworkError: If URL cannot be fetched
    """
    if not validate_url(url):
        raise InvalidURLError(f"Invalid URL format: {url}")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return str(response.text)
    except requests.exceptions.Timeout:
        raise NetworkError(f"Connection timed out while fetching {url}")
    except requests.exceptions.ConnectionError:
        raise NetworkError(f"Connection error while fetching {url}")
    except requests.exceptions.HTTPError as e:
        raise NetworkError(f"HTTP error {e.response.status_code} while fetching {url}")
    except requests.exceptions.RequestException as e:
        raise NetworkError(f"Error fetching {url}: {str(e)}")


def html_to_markdown(
    html: str,
    include_links: bool = True,
    include_images: bool = True,
    include_toc: bool = False,
    css_selector: Optional[str] = None,
    compact_output: bool = False,
) -> str:
    """Convert HTML to Markdown with various formatting options.

    This function takes HTML content and converts it to Markdown format.
    It provides several options to customize the output, including link/image
    handling, table of contents generation, content filtering, and whitespace
    management.

    Args:
        html: HTML content to convert as a string
        include_links: Whether to include hyperlinks (True) or convert them to
                     plain text (False)
        include_images: Whether to include images (True) or exclude them (False)
        include_toc: Whether to generate table of contents based on headings (True)
                    or not (False)
        css_selector: CSS selector to extract specific content from the HTML
                     (e.g., "main", "article"). If None, processes the entire HTML.
        compact_output: Whether to remove excessive blank lines in the output (True)
                       or preserve the original whitespace (False)

    Returns:
        A string containing the converted Markdown content

    Examples:
        >>> html = "<h1>Title</h1><p>Content with <a href='#'>link</a></p>"
        >>> print(html_to_markdown(html))
        # Title

        Content with [link](#)

        >>> print(html_to_markdown(html, include_links=False))
        # Title

        Content with link
    """
    # Extract specific content by CSS selector if provided
    if css_selector:
        soup = BeautifulSoup(html, "html.parser")
        selected = soup.select(css_selector)
        if selected:
            html = "".join(str(element) for element in selected)

    # Configure html2text
    h = html2text.HTML2Text()
    h.ignore_links = not include_links
    h.ignore_images = not include_images
    h.body_width = 0  # Don't wrap text

    markdown = h.handle(html)

    # Post-process the markdown
    import re

    # Remove zero-width spaces and other invisible characters
    markdown = re.sub(r"[\u200B\u200C\u200D\uFEFF]", "", markdown)

    # Post-process to remove excessive blank lines if requested
    if compact_output:
        # Replace 3 or more consecutive newlines with just 2
        markdown = re.sub(r"\n{3,}", "\n\n", markdown)

    # Add table of contents if requested
    if include_toc:
        headings = re.findall(r"^(#{1,6})\s+(.+)$", markdown, re.MULTILINE)

        if headings:
            toc = ["# Table of Contents\n"]
            for markers, title in headings:
                level = len(markers) - 1  # Adjust for 0-based indentation
                indent = "  " * level
                link = title.lower().replace(" ", "-")
                # Clean the link of non-alphanumeric characters
                link = re.sub(r"[^\w-]", "", link)
                toc.append(f"{indent}- [{title}](#{link})")

            markdown = "\n".join(toc) + "\n\n" + markdown

    # The return type is explicitly str, so we ensure it's returned as a string
    return str(markdown)


def convert_url_to_markdown(
    url: str,
    include_links: bool = True,
    include_images: bool = True,
    include_toc: bool = False,
    css_selector: Optional[str] = None,
    compact_output: bool = False,
) -> str:
    """Convert a web page to markdown.

    Args:
        url: URL of the web page
        include_links: Whether to include hyperlinks
        include_images: Whether to include images
        include_toc: Whether to generate table of contents
        css_selector: CSS selector to extract specific content
        compact_output: Whether to remove excessive blank lines

    Returns:
        Markdown content

    Raises:
        InvalidURLError: If URL format is invalid
        NetworkError: If URL cannot be fetched
    """
    html = fetch_url(url)
    return html_to_markdown(
        html,
        include_links=include_links,
        include_images=include_images,
        include_toc=include_toc,
        css_selector=css_selector,
        compact_output=compact_output,
    )
