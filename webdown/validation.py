"""Validation utilities for webdown.

This module provides centralized validation functions for various inputs
used throughout the webdown package.
"""

import urllib.parse
from typing import Optional

from bs4 import BeautifulSoup


def validate_url(url: str) -> str:
    """Validate a URL and return it if valid.

    Args:
        url: The URL to validate

    Returns:
        The validated URL

    Raises:
        ValueError: If the URL is invalid
    """
    if not url:
        raise ValueError("URL cannot be empty")

    parsed = urllib.parse.urlparse(url)

    # Check if URL has a scheme and netloc
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(
            f"Invalid URL: {url}. URL must include scheme "
            f"(http:// or https://) and domain."
        )

    # Ensure scheme is http or https
    if parsed.scheme not in ["http", "https"]:
        raise ValueError(
            f"Invalid URL scheme: {parsed.scheme}. Only http and https are supported."
        )

    return url


def validate_css_selector(selector: str) -> str:
    """Validate a CSS selector.

    Args:
        selector: The CSS selector to validate

    Returns:
        The validated CSS selector

    Raises:
        ValueError: If the selector is invalid
    """
    if not selector:
        raise ValueError("CSS selector cannot be empty")

    # Simple validation - just create a soup and try using the selector
    # This will raise a ValueError if the selector is invalid
    try:
        soup = BeautifulSoup("<html></html>", "html.parser")
        soup.select(selector)
        return selector
    except Exception as e:
        raise ValueError(f"Invalid CSS selector: {selector}. Error: {str(e)}")


def validate_body_width(width: Optional[int]) -> Optional[int]:
    """Validate body width parameter.

    Args:
        width: The body width to validate, or None for no width limit

    Returns:
        The validated body width or None

    Raises:
        ValueError: If the width is invalid
    """
    if width is None:
        return None

    # Ensure width is an integer and within reasonable range
    if not isinstance(width, int):
        raise ValueError(f"Body width must be an integer, got {type(width).__name__}")

    if width < 0:
        raise ValueError(f"Body width cannot be negative, got {width}")

    # Upper limit of 2000 is arbitrary but reasonable
    if width > 2000:
        raise ValueError(f"Body width too large, maximum is 2000, got {width}")

    return width


def validate_numeric_parameter(
    name: str,
    value: Optional[int],
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
) -> Optional[int]:
    """Validate a numeric parameter.

    Args:
        name: The name of the parameter (for error messages)
        value: The value to validate
        min_value: Optional minimum value
        max_value: Optional maximum value

    Returns:
        The validated value

    Raises:
        ValueError: If the value is invalid
    """
    if value is None:
        return None

    if not isinstance(value, int):
        raise ValueError(f"{name} must be an integer, got {type(value).__name__}")

    if min_value is not None and value < min_value:
        raise ValueError(f"{name} must be at least {min_value}, got {value}")

    if max_value is not None and value > max_value:
        raise ValueError(f"{name} must be at most {max_value}, got {value}")

    return value


def validate_string_parameter(
    name: str, value: Optional[str], allowed_values: Optional[list] = None
) -> Optional[str]:
    """Validate a string parameter.

    Args:
        name: The name of the parameter (for error messages)
        value: The value to validate
        allowed_values: Optional list of allowed values

    Returns:
        The validated value

    Raises:
        ValueError: If the value is invalid
    """
    if value is None:
        return None

    if not isinstance(value, str):
        raise ValueError(f"{name} must be a string, got {type(value).__name__}")

    if allowed_values is not None and value not in allowed_values:
        allowed_str = ", ".join(allowed_values)
        raise ValueError(f"{name} must be one of: {allowed_str}, got {value}")

    return value


def validate_boolean_parameter(name: str, value: Optional[bool]) -> Optional[bool]:
    """Validate a boolean parameter.

    Args:
        name: The name of the parameter (for error messages)
        value: The value to validate

    Returns:
        The validated value

    Raises:
        ValueError: If the value is invalid
    """
    if value is None:
        return None

    if not isinstance(value, bool):
        raise ValueError(f"{name} must be a boolean, got {type(value).__name__}")

    return value
