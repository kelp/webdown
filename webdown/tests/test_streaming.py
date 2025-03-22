"""Tests for streaming functionality with large documents."""

from unittest.mock import MagicMock, patch

import requests_mock

from webdown.config import WebdownConfig
from webdown.converter import convert_url_to_markdown
from webdown.html_parser import _check_streaming_needed, fetch_url


class TestStreamingFunctionality:
    """Tests for streaming functionality."""

    def test_check_streaming_needed(self) -> None:
        """Test that _check_streaming_needed detects large documents."""
        with requests_mock.Mocker() as m:
            # Mock head request for small document
            m.head("https://example.com/small", headers={"content-length": "100000"})

            # Mock head request for large document
            m.head("https://example.com/large", headers={"content-length": "15000000"})

            # Document below 10MB threshold should not trigger streaming
            result_small = _check_streaming_needed("https://example.com/small")
            assert result_small is False

            # Document above 10MB threshold should trigger streaming
            result_large = _check_streaming_needed("https://example.com/large")
            assert result_large is True

    @patch("requests.get")
    def test_streaming_for_large_documents(self, mock_get: MagicMock) -> None:
        """Test that streaming is used for large documents."""
        # Create a mock response with content-length > 10MB
        mock_response = MagicMock()
        mock_response.headers = {"content-length": "15000000"}

        # Create content that simulates an HTML page
        html_content = "<!DOCTYPE html><html><body><h1>Test</h1></body></html>"
        mock_response.iter_content.return_value = [html_content.encode("utf-8")]
        mock_get.return_value = mock_response

        # Patch the _check_streaming_needed function to return True
        with patch("webdown.html_parser._check_streaming_needed") as mock_check:
            mock_check.return_value = True

            # Test fetch_url
            result = fetch_url("https://example.com/large")

            # Verify streaming was used
            mock_get.assert_called_once()
            assert mock_get.call_args[1].get("stream") is True
            assert html_content in result

    @patch("requests.get")
    def test_streaming_progress_bar(self, mock_get: MagicMock) -> None:
        """Test that progress bar is shown when using streaming mode."""
        # Create a mock response
        mock_response = MagicMock()
        mock_response.headers = {"content-length": "15000000"}

        # Create HTML content chunks
        html_content = (
            "<!DOCTYPE html><html><body><h1>Test Streaming</h1></body></html>"
        )
        mock_response.iter_content.return_value = [html_content.encode("utf-8")]
        mock_get.return_value = mock_response

        # Patch tqdm
        with patch("webdown.html_parser.tqdm") as mock_tqdm:
            mock_tqdm_instance = MagicMock()
            # Properly setup the context manager return value
            mock_tqdm_instance.__enter__.return_value = mock_tqdm_instance
            mock_tqdm.return_value = mock_tqdm_instance

            # Test with show_progress=True
            result = fetch_url("https://example.com/large", show_progress=True)

            # Verify tqdm was used
            mock_tqdm.assert_called_once()
            # Verify update was called
            assert mock_tqdm_instance.update.called
            # Verify content is in result
            assert html_content in result

    def test_full_streaming_conversion(self) -> None:
        """Test the full streaming conversion pipeline."""
        # Use patches at the converter level
        html_content = "<html><body><h1>Large Document</h1></body></html>"
        markdown_content = "# Large Document"

        with (
            patch(
                "webdown.converter.fetch_url", return_value=html_content
            ) as mock_fetch,
            patch(
                "webdown.converter.html_to_markdown", return_value=markdown_content
            ) as mock_html_to_md,
        ):

            # Test the full pipeline
            config = WebdownConfig(url="https://example.com/large")
            result = convert_url_to_markdown(config)

            # Verify the function was called with the correct HTML
            mock_fetch.assert_called_once_with(
                "https://example.com/large", show_progress=False
            )
            mock_html_to_md.assert_called_once()

            # Check result
            assert result == markdown_content
