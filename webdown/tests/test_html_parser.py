"""Tests for HTML parser functionality."""

from unittest.mock import MagicMock, patch

import pytest
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from webdown.config import WebdownError
from webdown.error_utils import ErrorCode, handle_request_exception
from webdown.html_parser import (
    _check_streaming_needed,
    _create_progress_bar,
    _handle_small_response,
    _process_response_chunks,
    extract_content_with_css,
    fetch_url,
    fetch_url_with_progress,
    is_valid_url,
)


class TestURLValidation:
    """Tests for URL validation functions."""

    def test_is_valid_url(self) -> None:
        """Test valid and invalid URLs."""
        # Valid URLs
        assert is_valid_url("https://example.com") is True
        assert is_valid_url("http://example.com/path?q=test") is True

        # Invalid URLs
        assert is_valid_url("not_a_url") is False
        assert is_valid_url("ftp://example.com") is False
        assert is_valid_url("") is False


class TestProgressBar:
    """Tests for progress bar creation and handling."""

    def test_create_progress_bar(self) -> None:
        """Test creating progress bar."""
        # Test with known size
        bar = _create_progress_bar("https://example.com/file.html", 1000, True)
        assert isinstance(bar, tqdm)
        assert bar.total == 1000
        assert "Downloading file.html" in bar.desc
        assert bar.disable is False

        # Test with unknown size
        bar = _create_progress_bar("https://example.com/", 0, True)
        assert isinstance(bar, tqdm)
        assert bar.total is None
        assert "Downloading webpage" in bar.desc

        # Test with progress disabled
        bar = _create_progress_bar("https://example.com/file.html", 1000, False)
        assert bar.disable is True


class TestResponseProcessing:
    """Tests for response processing functions."""

    def test_process_response_chunks_bytes(self) -> None:
        """Test processing response chunks with bytes content."""
        # Setup mock response with byte chunks
        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b"chunk1", b"chunk2"]

        # Setup mock progress bar
        mock_bar = MagicMock()

        # Call function
        result = _process_response_chunks(mock_response, mock_bar, 1024)

        # Verify results
        assert result == "chunk1chunk2"
        assert mock_bar.update.call_count == 2

    def test_process_response_chunks_text(self) -> None:
        """Test processing response chunks with text content."""
        # Setup mock response with string chunks (this is uncommon but supported)
        mock_response = MagicMock()
        mock_response.iter_content.return_value = ["text1", "text2"]

        # Setup mock progress bar
        mock_bar = MagicMock()

        # Call function
        result = _process_response_chunks(mock_response, mock_bar, 1024)

        # Verify results
        assert result == "text1text2"
        assert mock_bar.update.call_count == 2

    def test_handle_small_response(self) -> None:
        """Test handling small response optimization."""
        # Small response with progress off should return text directly
        mock_small = MagicMock()
        mock_small.headers = {"content-length": "500"}
        mock_small.text = "small content"
        assert _handle_small_response(mock_small, False) == "small content"

        # Small response with progress on should return None (use streaming)
        mock_small_progress = MagicMock()
        mock_small_progress.headers = {"content-length": "500"}
        assert _handle_small_response(mock_small_progress, True) is None

        # Large response should return None (use streaming)
        mock_large = MagicMock()
        mock_large.headers = {"content-length": "2000000"}  # 2MB
        assert _handle_small_response(mock_large, False) is None

        # No content-length should return None (use streaming)
        mock_no_length = MagicMock()
        mock_no_length.headers = {}
        assert _handle_small_response(mock_no_length, False) is None


class TestRequestExceptionHandling:
    """Tests for request exception handling."""

    def test_handle_request_exception(self) -> None:
        """Test exception handling for requests."""
        url = "https://example.com"

        # Test timeout exception
        with pytest.raises(WebdownError) as exc_info:
            handle_request_exception(
                requests.exceptions.Timeout("Connection timed out"), url
            )
        assert exc_info.value.code == ErrorCode.NETWORK_TIMEOUT
        assert "Timeout error" in str(exc_info.value)

        # Test connection error
        with pytest.raises(WebdownError) as exc_info:
            handle_request_exception(
                requests.exceptions.ConnectionError("Connection refused"), url
            )
        assert exc_info.value.code == ErrorCode.NETWORK_CONNECTION
        assert "Connection error" in str(exc_info.value)


class TestFetching:
    """Tests for URL fetching functions."""

    @patch("webdown.html_parser.requests.get")
    def test_fetch_url_with_progress_small(self, mock_get: MagicMock) -> None:
        """Test fetching with optimization for small responses."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.headers = {"content-length": "500"}
        mock_response.text = "small content"
        mock_get.return_value = mock_response

        # Test fetch with small content
        result = fetch_url_with_progress("https://example.com", False)
        assert result == "small content"
        mock_get.assert_called_once()

    @patch("webdown.html_parser.requests.get")
    @patch("webdown.html_parser._process_response_chunks")
    def test_fetch_url_with_progress_streaming(
        self, mock_process: MagicMock, mock_get: MagicMock
    ) -> None:
        """Test fetching with streaming for larger responses."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.headers = {"content-length": "2000000"}  # 2MB
        mock_get.return_value = mock_response
        mock_process.return_value = "streamed content"

        # Test fetch with streaming
        result = fetch_url_with_progress("https://example.com", True)
        assert result == "streamed content"
        mock_get.assert_called_once()
        mock_process.assert_called_once()

    @patch("webdown.html_parser.requests.get")
    def test_fetch_url_with_progress_exception(self, mock_get: MagicMock) -> None:
        """Test handling exceptions during fetch."""
        # Setup mock to raise exception
        mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")

        # Test fetch with exception
        with pytest.raises(WebdownError) as exc_info:
            fetch_url_with_progress("https://example.com")
        assert exc_info.value.code == ErrorCode.NETWORK_TIMEOUT
        assert "Timeout error" in str(exc_info.value)

    @patch("webdown.html_parser.fetch_url_with_progress")
    def test_fetch_url(self, mock_fetch: MagicMock) -> None:
        """Test the simplified fetch_url wrapper."""
        mock_fetch.return_value = "content"

        # Test with valid URL
        result = fetch_url("https://example.com")
        assert result == "content"
        mock_fetch.assert_called_once()

        # Test with invalid URL
        with pytest.raises(WebdownError) as exc_info:
            fetch_url("invalid://url")
        assert exc_info.value.code == ErrorCode.URL_INVALID


class TestCssSelectors:
    """Tests for CSS selector functions."""

    def test_extract_content_with_css(self) -> None:
        """Test content extraction with CSS selectors."""
        html = """
        <html>
            <body>
                <div id="main">
                    <h1>Title</h1>
                    <p>Paragraph</p>
                </div>
                <div id="footer">Footer</div>
            </body>
        </html>
        """

        # Test valid selector with match
        result = extract_content_with_css(html, "#main")
        assert "Title" in result
        assert "Paragraph" in result
        assert "Footer" not in result

        # Test selector with no match (should return original HTML)
        with pytest.warns(UserWarning):
            result = extract_content_with_css(html, ".non-existent")
        assert "Title" in result
        assert "Footer" in result

        # Test invalid HTML
        with pytest.raises(WebdownError) as exc_info:
            # Create a mock BeautifulSoup.select that raises an exception
            with patch.object(
                BeautifulSoup, "select", side_effect=Exception("Parse error")
            ):
                extract_content_with_css("<malformed", "body")
        assert exc_info.value.code == ErrorCode.CSS_SELECTOR_INVALID
        assert "Error applying CSS selector" in str(exc_info.value)


class TestStreaming:
    """Tests for streaming-related functions."""

    @patch("webdown.html_parser.requests.head")
    def test_check_streaming_needed_small(self, mock_head: MagicMock) -> None:
        """Test checking if streaming is needed for small content."""
        # Setup mock for small content
        mock_response = MagicMock()
        mock_response.headers = {"content-length": "5000000"}  # 5MB
        mock_head.return_value = mock_response

        # Should return False for content under threshold
        assert _check_streaming_needed("https://example.com") is False

    @patch("webdown.html_parser.requests.head")
    def test_check_streaming_needed_large(self, mock_head: MagicMock) -> None:
        """Test checking if streaming is needed for large content."""
        # Setup mock for large content
        mock_response = MagicMock()
        mock_response.headers = {"content-length": "15000000"}  # 15MB
        mock_head.return_value = mock_response

        # Should return True for content over threshold
        assert _check_streaming_needed("https://example.com") is True

    @patch("webdown.html_parser.requests.head")
    def test_check_streaming_needed_no_length(self, mock_head: MagicMock) -> None:
        """Test checking if streaming is needed when content-length is missing."""
        # Setup mock for response without content-length
        mock_response = MagicMock()
        mock_response.headers = {}
        mock_head.return_value = mock_response

        # Should default to False when content-length is missing
        assert _check_streaming_needed("https://example.com") is False

    @patch("webdown.html_parser.requests.head")
    def test_check_streaming_needed_exception(self, mock_head: MagicMock) -> None:
        """Test checking if streaming is needed when request fails."""
        # Setup mock to raise exception
        mock_head.side_effect = requests.exceptions.RequestException("Error")

        # Should default to False on error
        assert _check_streaming_needed("https://example.com") is False
