"""HTML to Markdown conversion functionality."""

from typing import Optional
from urllib.parse import urlparse

import html2text
import requests
from bs4 import BeautifulSoup


class WebdownError(Exception):
    """Base exception for webdown errors."""

    pass


class NetworkError(WebdownError):
    """Exception raised for network-related errors."""

    pass


class InvalidURLError(WebdownError):
    """Exception raised for invalid URL format."""

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
) -> str:
    """Convert HTML to Markdown.

    Args:
        html: HTML content to convert
        include_links: Whether to include hyperlinks
        include_images: Whether to include images
        include_toc: Whether to generate table of contents
        css_selector: CSS selector to extract specific content

    Returns:
        Markdown content
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

    # Add table of contents if requested
    if include_toc:
        import re

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
) -> str:
    """Convert a web page to markdown.

    Args:
        url: URL of the web page
        include_links: Whether to include hyperlinks
        include_images: Whether to include images
        include_toc: Whether to generate table of contents
        css_selector: CSS selector to extract specific content

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
    )
