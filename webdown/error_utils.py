"""Error handling utilities for webdown.

This module provides centralized error handling utilities used throughout
the webdown package.
"""

from typing import NoReturn

import requests

from webdown.config import WebdownError


# Error codes for different types of errors
class ErrorCode:
    """Error codes for categorizing different types of errors.

    These codes allow for programmatic error handling and consistent
    error classification across the application.
    """

    # URL and network errors
    URL_INVALID = "URL_INVALID"
    NETWORK_TIMEOUT = "NETWORK_TIMEOUT"
    NETWORK_CONNECTION = "NETWORK_CONNECTION"
    HTTP_ERROR = "HTTP_ERROR"
    REQUEST_ERROR = "REQUEST_ERROR"

    # File-related errors
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    IO_ERROR = "IO_ERROR"

    # Validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    CSS_SELECTOR_INVALID = "CSS_SELECTOR_INVALID"
    PARAMETER_INVALID = "PARAMETER_INVALID"

    # Parsing errors
    HTML_PARSE_ERROR = "HTML_PARSE_ERROR"
    MARKDOWN_PARSE_ERROR = "MARKDOWN_PARSE_ERROR"
    XML_PARSE_ERROR = "XML_PARSE_ERROR"

    # Configuration errors
    CONFIG_ERROR = "CONFIG_ERROR"

    # Crawler errors
    CRAWL_SCOPE_ERROR = "CRAWL_SCOPE_ERROR"
    OUTPUT_DIR_ERROR = "OUTPUT_DIR_ERROR"
    SITEMAP_PARSE_ERROR = "SITEMAP_PARSE_ERROR"

    # Unexpected errors
    UNEXPECTED_ERROR = "UNEXPECTED_ERROR"


def handle_request_exception(exception: Exception, url: str) -> NoReturn:
    """Handle a request exception and raise a WebdownError with appropriate message.

    Args:
        exception: The exception to handle
        url: The URL that was requested

    Raises:
        WebdownError: Always raised with appropriate message
    """
    if isinstance(exception, requests.exceptions.Timeout):
        raise WebdownError(
            f"Timeout error fetching {url}. The server took too long to respond.",
            code=ErrorCode.NETWORK_TIMEOUT,
        )
    elif isinstance(exception, requests.exceptions.ConnectionError):
        raise WebdownError(
            f"Connection error fetching {url}. Please check your internet connection.",
            code=ErrorCode.NETWORK_CONNECTION,
        )
    elif isinstance(exception, requests.exceptions.HTTPError):
        # Extract status code if available
        status_code = None
        if hasattr(exception, "response") and hasattr(
            exception.response, "status_code"
        ):
            status_code = exception.response.status_code

        status_msg = f" (Status code: {status_code})" if status_code else ""
        raise WebdownError(
            f"HTTP error fetching {url}{status_msg}. The server returned an error.",
            code=ErrorCode.HTTP_ERROR,
        )
    else:
        # Generic RequestException or any other exception
        raise WebdownError(
            f"Error fetching {url}: {str(exception)}",
            code=ErrorCode.REQUEST_ERROR,
        )


def handle_validation_error(
    message: str, code: str = ErrorCode.VALIDATION_ERROR
) -> NoReturn:
    """Handle a validation error and raise a WebdownError.

    Args:
        message: Error message
        code: Error code

    Raises:
        WebdownError: Always raised with appropriate message
    """
    raise WebdownError(message, code=code)


def get_friendly_error_message(error: Exception) -> str:
    """Get a user-friendly error message for an exception.

    This function is intended for CLI and user-facing interfaces.

    Args:
        error: The exception to get a message for

    Returns:
        A user-friendly error message
    """
    # For WebdownError, we already have a good message
    if isinstance(error, WebdownError):
        # Handle URL validation errors specially for better UX
        message = str(error)
        if hasattr(error, "code") and error.code == ErrorCode.URL_INVALID:
            message += (
                "\nPlease make sure the URL includes a valid protocol "
                "and domain (like https://example.com)."
            )
        return message

    # For other exceptions, provide a generic message
    return f"An unexpected error occurred: {str(error)}"


def format_error_for_cli(error: Exception) -> str:
    """Format an error message for CLI output.

    Args:
        error: The exception to format

    Returns:
        A formatted error message for CLI output
    """
    friendly_message = get_friendly_error_message(error)

    # For CLI, prefix with "Error: " and format nicely
    lines = friendly_message.split("\n")
    if len(lines) == 1:
        return f"Error: {friendly_message}"

    # For multi-line messages, format with indentation
    result = ["Error:"]
    for line in lines:
        result.append(f"  {line}")

    return "\n".join(result)
