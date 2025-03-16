"""Tests for error handling in webdown."""

import pytest
import requests
import requests_mock

from webdown.converter import WebdownError, fetch_url, validate_url


class TestErrorHandling:
    """Tests for error handling in webdown."""

    def test_validate_url(self) -> None:
        """Test URL validation."""
        # Valid URLs
        assert validate_url("https://example.com") is True
        assert validate_url("http://example.com/page") is True
        assert validate_url("https://subdomain.example.com/path?query=value") is True

        # Invalid URLs
        assert validate_url("not_a_url") is False
        assert validate_url("example.com") is False  # No scheme
        assert validate_url("https://") is False  # No host

    def test_fetch_url_invalid_url(self) -> None:
        """Test fetch_url with invalid URL."""
        with pytest.raises(WebdownError) as excinfo:
            fetch_url("not_a_valid_url")

        assert "Invalid URL format" in str(excinfo.value)

    def test_fetch_url_connection_timeout(self) -> None:
        """Test fetch_url with connection timeout."""
        with requests_mock.Mocker() as m:
            m.get("https://example.com", exc=requests.exceptions.Timeout)

            with pytest.raises(WebdownError) as excinfo:
                fetch_url("https://example.com")

            assert "Connection timed out" in str(excinfo.value)

    def test_fetch_url_connection_error(self) -> None:
        """Test fetch_url with connection error."""
        with requests_mock.Mocker() as m:
            m.get("https://example.com", exc=requests.exceptions.ConnectionError)

            with pytest.raises(WebdownError) as excinfo:
                fetch_url("https://example.com")

            assert "Connection error" in str(excinfo.value)

    def test_fetch_url_http_error(self) -> None:
        """Test fetch_url with HTTP error."""
        with requests_mock.Mocker() as m:
            m.get("https://example.com", status_code=404)

            with pytest.raises(WebdownError) as excinfo:
                fetch_url("https://example.com")

            assert "HTTP error 404" in str(excinfo.value)

    def test_fetch_url_request_exception(self) -> None:
        """Test fetch_url with generic request exception."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://example.com",
                exc=requests.exceptions.RequestException("Custom error"),
            )

            with pytest.raises(WebdownError) as excinfo:
                fetch_url("https://example.com")

            assert "Error fetching" in str(excinfo.value)
            assert "Custom error" in str(excinfo.value)

    def test_fetch_url_with_progress(self) -> None:
        """Test fetch_url with progress bar."""
        with requests_mock.Mocker() as m:
            # Mock the HEAD request first for content length
            m.head("https://example.com", headers={"content-length": "1000"})
            # Then mock the GET request
            m.get("https://example.com", text="<html>Test content</html>")

            # This should not raise any exceptions
            content = fetch_url("https://example.com", show_progress=True)
            assert "<html>Test content</html>" == content
