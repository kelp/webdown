"""Tests for error utilities."""

# mypy: disable-error-code="no-untyped-def"
import pytest
import requests
from requests import Response

from webdown.config import WebdownError
from webdown.error_utils import (
    ErrorCode,
    format_error_for_cli,
    get_friendly_error_message,
    handle_request_exception,
    handle_validation_error,
)


class TestHandleValidationError:
    """Tests for handle_validation_error function."""

    def test_handle_validation_error_default_code(self):
        """Test handle_validation_error with default error code."""
        with pytest.raises(WebdownError) as exc_info:
            handle_validation_error("Test validation error")

        assert exc_info.value.code == ErrorCode.VALIDATION_ERROR
        assert str(exc_info.value) == "Test validation error"

    def test_handle_validation_error_custom_code(self):
        """Test handle_validation_error with custom error code."""
        with pytest.raises(WebdownError) as exc_info:
            handle_validation_error(
                "CSS selector error", code=ErrorCode.CSS_SELECTOR_INVALID
            )

        assert exc_info.value.code == ErrorCode.CSS_SELECTOR_INVALID
        assert str(exc_info.value) == "CSS selector error"


class TestGetFriendlyErrorMessage:
    """Tests for get_friendly_error_message function."""

    def test_with_url_invalid_error(self):
        """Test with URL_INVALID error code."""
        error = WebdownError("Invalid URL: example", code=ErrorCode.URL_INVALID)
        message = get_friendly_error_message(error)

        assert "Invalid URL: example" in message
        assert "Please make sure the URL includes a valid protocol" in message
        assert "https://example.com" in message

    def test_with_regular_webdown_error(self):
        """Test with regular WebdownError."""
        error = WebdownError("Network error", code=ErrorCode.NETWORK_CONNECTION)
        message = get_friendly_error_message(error)

        assert message == "Network error"
        assert "Please make sure" not in message

    def test_with_generic_exception(self):
        """Test with generic exception."""
        error = ValueError("Invalid value")
        message = get_friendly_error_message(error)

        assert message == "An unexpected error occurred: Invalid value"


class TestFormatErrorForCli:
    """Tests for format_error_for_cli function."""

    def test_single_line_message(self):
        """Test with single line error message."""
        error = ValueError("Simple error")
        formatted = format_error_for_cli(error)

        assert formatted == "Error: An unexpected error occurred: Simple error"

    def test_multi_line_message(self):
        """Test with multi-line error message."""
        # Create a multi-line error message
        error = WebdownError("First line\nSecond line\nThird line")
        formatted = format_error_for_cli(error)

        assert formatted.startswith("Error:")
        assert "  First line" in formatted
        assert "  Second line" in formatted
        assert "  Third line" in formatted

        # Verify the formatting structure
        lines = formatted.split("\n")
        assert len(lines) == 4
        assert lines[0] == "Error:"
        assert lines[1] == "  First line"
        assert lines[2] == "  Second line"
        assert lines[3] == "  Third line"


class TestHandleRequestException:
    """Tests for handle_request_exception function."""

    def test_timeout_exception(self):
        """Test handling timeout exception."""
        exception = requests.exceptions.Timeout("Connection timed out")
        url = "https://example.com"

        with pytest.raises(WebdownError) as exc_info:
            handle_request_exception(exception, url)

        assert exc_info.value.code == ErrorCode.NETWORK_TIMEOUT
        assert "Timeout error fetching" in str(exc_info.value)
        assert url in str(exc_info.value)

    def test_connection_error(self):
        """Test handling connection error."""
        exception = requests.exceptions.ConnectionError("Connection refused")
        url = "https://example.com"

        with pytest.raises(WebdownError) as exc_info:
            handle_request_exception(exception, url)

        assert exc_info.value.code == ErrorCode.NETWORK_CONNECTION
        assert "Connection error fetching" in str(exc_info.value)
        assert url in str(exc_info.value)

    def test_http_error_with_status_code(self):
        """Test handling HTTP error with status code."""
        # Create a response with a status code
        response = Response()
        response.status_code = 404

        # Create an HTTPError with the response
        exception = requests.exceptions.HTTPError("404 Not Found", response=response)
        url = "https://example.com"

        with pytest.raises(WebdownError) as exc_info:
            handle_request_exception(exception, url)

        assert exc_info.value.code == ErrorCode.HTTP_ERROR
        assert "HTTP error fetching" in str(exc_info.value)
        assert "Status code: 404" in str(exc_info.value)
        assert url in str(exc_info.value)

    def test_generic_request_exception(self):
        """Test handling generic request exception."""
        exception = requests.exceptions.RequestException("Unknown error")
        url = "https://example.com"

        with pytest.raises(WebdownError) as exc_info:
            handle_request_exception(exception, url)

        assert exc_info.value.code == ErrorCode.REQUEST_ERROR
        assert "Error fetching" in str(exc_info.value)
        assert "Unknown error" in str(exc_info.value)
        assert url in str(exc_info.value)
