"""Tests for validation utilities."""

from typing import Any

import pytest
from bs4 import BeautifulSoup

from webdown.validation import (
    validate_body_width,
    validate_boolean_parameter,
    validate_css_selector,
    validate_numeric_parameter,
    validate_string_parameter,
    validate_url,
)


class TestURLValidation:
    """Tests for URL validation."""

    def test_valid_urls(self) -> None:
        """Test valid URLs."""
        assert validate_url("https://example.com") == "https://example.com"
        assert validate_url("http://example.com") == "http://example.com"
        assert validate_url("https://example.com/path") == "https://example.com/path"
        assert (
            validate_url("https://example.com/path?query=value")
            == "https://example.com/path?query=value"
        )
        assert (
            validate_url("https://user:pass@example.com")
            == "https://user:pass@example.com"
        )

    def test_empty_url(self) -> None:
        """Test empty URL."""
        with pytest.raises(ValueError, match="URL cannot be empty"):
            validate_url("")

    def test_missing_scheme(self) -> None:
        """Test URL with missing scheme."""
        with pytest.raises(ValueError, match="Invalid URL"):
            validate_url("example.com")

    def test_missing_netloc(self) -> None:
        """Test URL with missing netloc."""
        with pytest.raises(ValueError, match="Invalid URL"):
            validate_url("http://")

    def test_unsupported_scheme(self) -> None:
        """Test URL with unsupported scheme."""
        with pytest.raises(ValueError, match="Invalid URL scheme"):
            validate_url("ftp://example.com")


class TestCSSSelector:
    """Tests for CSS selector validation."""

    def test_valid_selectors(self) -> None:
        """Test valid CSS selectors."""
        assert validate_css_selector("body") == "body"
        assert validate_css_selector("#main") == "#main"
        assert validate_css_selector(".content") == ".content"
        assert validate_css_selector("div.content") == "div.content"
        assert validate_css_selector("div > p") == "div > p"

    def test_empty_selector(self) -> None:
        """Test empty CSS selector."""
        with pytest.raises(ValueError, match="CSS selector cannot be empty"):
            validate_css_selector("")

    def test_invalid_selector(self) -> None:
        """Test invalid CSS selector."""
        # Patch BeautifulSoup.select to raise an exception
        original_select = BeautifulSoup.select

        def mock_select(self: Any, selector: str) -> list:
            if selector == "invalid[":
                raise Exception("Invalid selector")
            return original_select(self, selector)  # pragma: no cover

        BeautifulSoup.select = mock_select  # type: ignore

        try:
            with pytest.raises(ValueError, match="Invalid CSS selector"):
                validate_css_selector("invalid[")
        finally:
            # Restore original method
            BeautifulSoup.select = original_select  # type: ignore


class TestBodyWidth:
    """Tests for body width validation."""

    def test_none_width(self) -> None:
        """Test None width."""
        assert validate_body_width(None) is None

    def test_valid_width(self) -> None:
        """Test valid width values."""
        assert validate_body_width(0) == 0
        assert validate_body_width(80) == 80
        assert validate_body_width(2000) == 2000

    def test_non_integer_width(self) -> None:
        """Test non-integer width."""
        with pytest.raises(ValueError, match="must be an integer"):
            validate_body_width("80")  # type: ignore

    def test_negative_width(self) -> None:
        """Test negative width."""
        with pytest.raises(ValueError, match="cannot be negative"):
            validate_body_width(-1)

    def test_too_large_width(self) -> None:
        """Test width that is too large."""
        with pytest.raises(ValueError, match="too large"):
            validate_body_width(2001)


class TestNumericParameter:
    """Tests for numeric parameter validation."""

    def test_none_value(self) -> None:
        """Test None value."""
        assert validate_numeric_parameter("test", None) is None

    def test_valid_values(self) -> None:
        """Test valid numeric values."""
        assert validate_numeric_parameter("test", 0) == 0
        assert validate_numeric_parameter("test", 10) == 10
        assert validate_numeric_parameter("test", -10) == -10

    def test_min_value(self) -> None:
        """Test minimum value constraint."""
        assert validate_numeric_parameter("test", 5, min_value=5) == 5
        assert validate_numeric_parameter("test", 10, min_value=5) == 10

        with pytest.raises(ValueError, match="must be at least 5"):
            validate_numeric_parameter("test", 4, min_value=5)

    def test_max_value(self) -> None:
        """Test maximum value constraint."""
        assert validate_numeric_parameter("test", 5, max_value=10) == 5
        assert validate_numeric_parameter("test", 10, max_value=10) == 10

        with pytest.raises(ValueError, match="must be at most 10"):
            validate_numeric_parameter("test", 11, max_value=10)

    def test_min_and_max_value(self) -> None:
        """Test both minimum and maximum constraints."""
        assert validate_numeric_parameter("test", 5, min_value=0, max_value=10) == 5
        assert validate_numeric_parameter("test", 0, min_value=0, max_value=10) == 0
        assert validate_numeric_parameter("test", 10, min_value=0, max_value=10) == 10

        with pytest.raises(ValueError, match="must be at least 0"):
            validate_numeric_parameter("test", -1, min_value=0, max_value=10)

        with pytest.raises(ValueError, match="must be at most 10"):
            validate_numeric_parameter("test", 11, min_value=0, max_value=10)

    def test_non_integer_value(self) -> None:
        """Test non-integer value."""
        with pytest.raises(ValueError, match="must be an integer"):
            validate_numeric_parameter("test", "5")  # type: ignore


class TestStringParameter:
    """Tests for string parameter validation."""

    def test_none_value(self) -> None:
        """Test None value."""
        assert validate_string_parameter("test", None) is None

    def test_valid_string(self) -> None:
        """Test valid string values."""
        assert validate_string_parameter("test", "") == ""
        assert validate_string_parameter("test", "hello") == "hello"

    def test_allowed_values(self) -> None:
        """Test string with allowed values constraint."""
        allowed = ["a", "b", "c"]
        assert validate_string_parameter("test", "a", allowed_values=allowed) == "a"
        assert validate_string_parameter("test", "b", allowed_values=allowed) == "b"
        assert validate_string_parameter("test", "c", allowed_values=allowed) == "c"

        with pytest.raises(ValueError, match="must be one of"):
            validate_string_parameter("test", "d", allowed_values=allowed)

    def test_non_string_value(self) -> None:
        """Test non-string value."""
        with pytest.raises(ValueError, match="must be a string"):
            validate_string_parameter("test", 5)  # type: ignore


class TestBooleanParameter:
    """Tests for boolean parameter validation."""

    def test_none_value(self) -> None:
        """Test None value."""
        assert validate_boolean_parameter("test", None) is None

    def test_valid_boolean(self) -> None:
        """Test valid boolean values."""
        assert validate_boolean_parameter("test", True) is True
        assert validate_boolean_parameter("test", False) is False

    def test_non_boolean_value(self) -> None:
        """Test non-boolean value."""
        with pytest.raises(ValueError, match="must be a boolean"):
            validate_boolean_parameter("test", "true")  # type: ignore

        with pytest.raises(ValueError, match="must be a boolean"):
            validate_boolean_parameter("test", 1)  # type: ignore

        with pytest.raises(ValueError, match="must be a boolean"):
            validate_boolean_parameter("test", 0)  # type: ignore
