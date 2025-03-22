"""HTML parsing and fetching functionality.

This module handles fetching web content and basic HTML parsing:
- URL validation and verification
- HTML fetching with proper error handling and progress tracking
- Content extraction with CSS selectors
- Streaming support for large web pages

The primary functions are fetch_url() for retrieving HTML content
and extract_content_with_css() for selecting specific parts of HTML.
"""

import io
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from webdown.config import WebdownError


def validate_url(url: str) -> bool:
    """Validate URL format.

    Args:
        url: URL to validate

    Returns:
        True if valid, False otherwise

    >>> validate_url('https://example.com')
    True
    >>> validate_url('http://example.com')
    True
    >>> validate_url('not_a_url')
    False
    """
    if not isinstance(url, str):
        return False

    if not url.strip():
        return False

    parsed = urlparse(url)

    # Check for required components
    has_scheme = bool(parsed.scheme)
    has_netloc = bool(parsed.netloc)

    return has_scheme and has_netloc


def _create_progress_bar(url: str, total_size: int, show_progress: bool) -> tqdm:
    """Create a progress bar for downloading content.

    Args:
        url: URL being downloaded
        total_size: Total size in bytes (0 if unknown)
        show_progress: Whether to display the progress bar

    Returns:
        Configured tqdm progress bar instance
    """
    # Extract page name for the progress description
    page_name = url.split("/")[-1] or "webpage"

    # Create progress bar - if content-length is unknown (0),
    # tqdm will show a progress bar without the total
    return tqdm(
        total=total_size if total_size > 0 else None,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
        desc=f"Downloading {page_name}",
        disable=not show_progress,
    )


def _process_response_chunks(
    response: requests.Response, progress_bar: tqdm, chunk_size: int
) -> str:
    """Process response chunks and update progress bar.

    Args:
        response: The HTTP response object
        progress_bar: Progress bar to update
        chunk_size: Size of chunks to read in bytes

    Returns:
        Complete response content as string
    """
    # Create a buffer to store the content
    content = io.StringIO()

    # Process chunks consistently, handling both str and bytes
    for chunk in response.iter_content(chunk_size=chunk_size):
        if chunk:
            # Calculate chunk size for progress bar
            chunk_len = (
                len(chunk) if isinstance(chunk, bytes) else len(chunk.encode("utf-8"))
            )
            # Decode bytes for StringIO if needed
            text_chunk = (
                chunk.decode("utf-8", errors="replace")
                if isinstance(chunk, bytes)
                else chunk
            )

            # Update progress with correct size
            progress_bar.update(chunk_len)
            # Store in string buffer
            content.write(text_chunk)

    return content.getvalue()


def _handle_small_response(
    response: requests.Response, show_progress: bool
) -> Optional[str]:
    """Handle small responses without streaming for better performance.

    Args:
        response: HTTP response object
        show_progress: Whether progress bar is requested

    Returns:
        Response text for small content, None otherwise
    """
    # Skip streaming for non-progress requests with small content
    if not show_progress and "content-length" in response.headers:
        content_length = int(response.headers.get("content-length", 0))
        if content_length < 1024 * 1024:  # 1MB
            return response.text
    return None


def _handle_request_exception(e: Exception, url: str) -> None:
    """Convert request exceptions to WebdownError with appropriate messages.

    Args:
        e: The exception that was raised
        url: The URL being fetched

    Raises:
        WebdownError: With appropriate error message
    """
    if isinstance(e, requests.exceptions.Timeout):
        raise WebdownError(f"Connection timed out while fetching {url}")
    elif isinstance(e, requests.exceptions.ConnectionError):
        raise WebdownError(f"Connection error while fetching {url}")
    elif isinstance(e, requests.exceptions.HTTPError):
        raise WebdownError(f"HTTP error {e.response.status_code} while fetching {url}")
    else:
        raise WebdownError(f"Error fetching {url}: {str(e)}")


def fetch_url_with_progress(
    url: str, show_progress: bool = False, chunk_size: int = 1024, timeout: int = 10
) -> str:
    """Fetch content from URL with streaming and optional progress bar.

    Args:
        url: URL to fetch
        show_progress: Whether to display a progress bar during download
        chunk_size: Size of chunks to read in bytes
        timeout: Request timeout in seconds

    Returns:
        Content as string

    Raises:
        WebdownError: If content cannot be fetched
    """
    # Note: URL validation is now centralized in _get_normalized_config
    # We assume URL is already validated when this function is called

    try:
        # Make a GET request with stream=True for both cases
        response = requests.get(url, timeout=timeout, stream=True)
        response.raise_for_status()

        # Try to handle small responses without streaming for performance
        small_response = _handle_small_response(response, show_progress)
        if small_response is not None:
            return small_response

        # For larger responses or when progress is requested, use streaming
        total_size = int(response.headers.get("content-length", 0))
        with _create_progress_bar(url, total_size, show_progress) as progress_bar:
            return _process_response_chunks(response, progress_bar, chunk_size)

    except (
        requests.exceptions.Timeout,
        requests.exceptions.ConnectionError,
        requests.exceptions.HTTPError,
        requests.exceptions.RequestException,
    ) as e:
        # This function raises a WebdownError with appropriate message
        _handle_request_exception(e, url)
        # The line below is never reached but needed for type checking
        raise RuntimeError("This should never be reached")


def fetch_url(url: str, show_progress: bool = False) -> str:
    """Fetch HTML content from URL with optional progress bar.

    This is a simplified wrapper around fetch_url_with_progress with default parameters.

    Args:
        url: URL to fetch
        show_progress: Whether to display a progress bar during download

    Returns:
        HTML content as string

    Raises:
        WebdownError: If URL is invalid or content cannot be fetched
    """
    # Validate URL for backward compatibility with tests
    # In normal usage, URL is already validated by _get_normalized_config
    if not validate_url(url):
        raise WebdownError(f"Invalid URL format: {url}")

    return fetch_url_with_progress(url, show_progress, chunk_size=1024, timeout=10)


def validate_css_selector(css_selector: str) -> None:
    """Validate CSS selector format and syntax.

    Args:
        css_selector: CSS selector to validate

    Raises:
        WebdownError: If the selector is invalid
    """
    if not isinstance(css_selector, str) or not css_selector.strip():
        raise WebdownError("CSS selector must be a non-empty string")

    # Basic validation to catch obvious syntax errors
    invalid_chars = ["<", ">", "(", ")", "@"]
    if any(char in css_selector for char in invalid_chars):
        raise WebdownError(
            f"Invalid CSS selector: '{css_selector}'. Contains invalid characters."
        )


def extract_content_with_css(html: str, css_selector: str) -> str:
    """Extract specific content from HTML using a CSS selector.

    CSS selector is assumed to be already validated before this function is called.

    Args:
        html: HTML content
        css_selector: CSS selector to extract content (pre-validated)

    Returns:
        HTML content of selected elements

    Raises:
        WebdownError: If there is an error applying the selector
    """
    import warnings

    # Note: No validation here - validation is now centralized in html_to_markdown

    try:
        soup = BeautifulSoup(html, "html.parser")
        selected = soup.select(css_selector)
        if selected:
            return "".join(str(element) for element in selected)
        else:
            # Warning - no elements matched
            warnings.warn(f"CSS selector '{css_selector}' did not match any elements")
            return html
    except Exception as e:
        raise WebdownError(f"Error applying CSS selector '{css_selector}': {str(e)}")


def _check_streaming_needed(url: str) -> bool:
    """Check if streaming is needed based on content size.

    Args:
        url: URL to check (assumed to be already validated)

    Returns:
        True if streaming should be used, False otherwise
    """
    # Fixed streaming threshold at 10MB
    STREAM_THRESHOLD = 10 * 1024 * 1024

    try:
        # Use HEAD request to check content length without full download
        head_response = requests.head(url, timeout=5)
        content_length = int(head_response.headers.get("content-length", "0"))
        return content_length > STREAM_THRESHOLD
    except (requests.RequestException, ValueError):
        # If HEAD request fails or content-length is invalid,
        # default to False (non-streaming) as a safe fallback
        return False
