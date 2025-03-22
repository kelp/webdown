"""Tests for converter module."""

from unittest.mock import MagicMock, patch

import pytest

from webdown.config import WebdownConfig, WebdownError
from webdown.converter import convert_url_to_markdown
from webdown.error_utils import ErrorCode
from webdown.html_parser import fetch_url
from webdown.markdown_converter import html_to_markdown
from webdown.validation import validate_url


class TestValidateUrl:
    """Tests for validate_url function."""

    def test_valid_url(self) -> None:
        """Test validation of valid URLs."""
        # Validates without raising exception
        assert validate_url("https://example.com") == "https://example.com"
        assert validate_url("http://example.com") == "http://example.com"
        assert validate_url("https://example.com/path") == "https://example.com/path"
        assert (
            validate_url("http://example.com/path?query=value")
            == "http://example.com/path?query=value"
        )

    def test_invalid_url(self) -> None:
        """Test validation of invalid URLs."""
        with pytest.raises(ValueError):
            validate_url("not_a_url")
        with pytest.raises(ValueError):
            validate_url("example.com")
        with pytest.raises(ValueError):
            validate_url("file:///path/to/file")  # File URLs should be rejected


class TestFetchUrl:
    """Tests for fetch_url function."""

    def test_invalid_url_raises_error(self) -> None:
        """Test that invalid URLs raise WebdownError."""
        with pytest.raises(WebdownError) as exc_info:
            fetch_url("not_a_url")
        assert "Invalid URL:" in str(exc_info.value)
        assert exc_info.value.code == ErrorCode.URL_INVALID

    @patch("webdown.html_parser.requests.get")
    def test_request_exceptions_raise_webdown_error(self, mock_get: MagicMock) -> None:
        """Test that request exceptions raise WebdownError."""
        import requests

        # Test timeout
        mock_get.side_effect = requests.exceptions.Timeout
        with pytest.raises(WebdownError) as exc_info:
            fetch_url("https://example.com")
        assert "timeout error" in str(exc_info.value).lower()
        assert exc_info.value.code == ErrorCode.NETWORK_TIMEOUT

        # Test connection error
        mock_get.side_effect = requests.exceptions.ConnectionError
        with pytest.raises(WebdownError) as exc_info:
            fetch_url("https://example.com")
        assert "connection error" in str(exc_info.value).lower()

        # Test HTTP error
        response_mock = MagicMock()
        response_mock.status_code = 404
        mock_get.side_effect = requests.exceptions.HTTPError(response=response_mock)
        with pytest.raises(WebdownError) as exc_info:
            fetch_url("https://example.com")
        assert "http error" in str(exc_info.value).lower()
        assert "404" in str(exc_info.value)

        # Test generic request exception
        mock_get.side_effect = requests.exceptions.RequestException("generic error")
        with pytest.raises(WebdownError) as exc_info:
            fetch_url("https://example.com")
        assert "error fetching" in str(exc_info.value).lower()
        assert "generic error" in str(exc_info.value)

    @patch("webdown.html_parser.requests.get")
    def test_successful_fetch(self, mock_get: MagicMock) -> None:
        """Test successful fetch returns HTML content."""
        # Set up mock response with content-length for non-streaming path
        mock_response = MagicMock()
        mock_response.text = "<html><body>Test</body></html>"
        mock_response.headers = {
            "content-length": "100"
        }  # Small content to trigger non-streaming path
        mock_get.return_value = mock_response

        result = fetch_url("https://example.com")
        assert result == "<html><body>Test</body></html>"
        mock_get.assert_called_once_with("https://example.com", timeout=10, stream=True)

    @patch("webdown.html_parser.requests.get")
    @patch("webdown.html_parser.tqdm")
    def test_fetch_url_with_progress_bar(
        self, mock_tqdm: MagicMock, mock_get: MagicMock
    ) -> None:
        """Test fetch_url with progress bar."""
        # Mock GET response
        mock_get_response = MagicMock()
        mock_get_response.headers = {"content-length": "1000"}
        mock_get_response.iter_content.return_value = ["chunk1", "chunk2", "chunk3"]
        mock_get.return_value = mock_get_response

        # Mock tqdm context manager
        mock_progress = MagicMock()
        mock_tqdm.return_value.__enter__.return_value = mock_progress

        # Call the function with progress bar
        _ = fetch_url("https://example.com", show_progress=True)

        # Verify the GET request was made with stream=True
        mock_get.assert_called_once_with("https://example.com", timeout=10, stream=True)

        # Verify tqdm was initialized with the correct total size
        mock_tqdm.assert_called_once()
        assert mock_tqdm.call_args[1]["total"] == 1000

        # Verify progress bar was updated for each chunk
        assert mock_progress.update.call_count == 3


class TestHtmlToMarkdown:
    """Tests for html_to_markdown function."""

    def test_basic_conversion(self) -> None:
        """Test basic HTML to Markdown conversion."""
        html = "<h1>Title</h1><p>Paragraph</p>"
        config = WebdownConfig()
        result = html_to_markdown(html, config)
        assert "# Title" in result
        assert "Paragraph" in result

    @patch("webdown.markdown_converter.html2text.HTML2Text")
    def test_link_options(self, mock_html2text_class: MagicMock) -> None:
        """Test link inclusion/exclusion options."""
        mock_html2text = MagicMock()
        mock_html2text_class.return_value = mock_html2text
        mock_html2text.handle.return_value = "Markdown content"

        # Test links included (default)
        config = WebdownConfig()
        html_to_markdown("<html><body>Test</body></html>", config)
        assert mock_html2text.ignore_links is False

        # Test links excluded
        config = WebdownConfig(include_links=False)
        html_to_markdown("<html><body>Test</body></html>", config)
        assert mock_html2text.ignore_links is True

    @patch("webdown.markdown_converter.html2text.HTML2Text")
    def test_image_options(self, mock_html2text_class: MagicMock) -> None:
        """Test image inclusion/exclusion options."""
        mock_html2text = MagicMock()
        mock_html2text_class.return_value = mock_html2text
        mock_html2text.handle.return_value = "Markdown content"

        # Test images included (default)
        config = WebdownConfig()
        html_to_markdown("<html><body>Test</body></html>", config)
        assert mock_html2text.ignore_images is False

        # Test images excluded
        config = WebdownConfig(include_images=False)
        html_to_markdown("<html><body>Test</body></html>", config)
        assert mock_html2text.ignore_images is True

    @patch("webdown.markdown_converter.html2text.HTML2Text")
    def test_body_width(self, mock_html2text_class: MagicMock) -> None:
        """Test body_width parameter."""
        mock_html2text = MagicMock()
        mock_html2text_class.return_value = mock_html2text
        mock_html2text.handle.return_value = "Markdown content"

        # Test default body_width (0)
        config = WebdownConfig()
        html_to_markdown("<html><body>Test</body></html>", config)
        assert mock_html2text.body_width == 0

        # Test custom body_width
        config = WebdownConfig(body_width=80)
        html_to_markdown("<html><body>Test</body></html>", config)
        assert mock_html2text.body_width == 80

        # Test another custom body_width
        config = WebdownConfig(body_width=72)
        html_to_markdown("<html><body>Test</body></html>", config)
        assert mock_html2text.body_width == 72

    @patch("webdown.html_parser.BeautifulSoup")
    @patch("webdown.markdown_converter.html2text.HTML2Text")
    def test_css_selector(
        self, mock_html2text_class: MagicMock, mock_beautiful_soup: MagicMock
    ) -> None:
        """Test CSS selector extraction."""
        mock_html2text = MagicMock()
        mock_html2text_class.return_value = mock_html2text
        mock_html2text.handle.return_value = "Markdown content"

        # Setup BeautifulSoup mock
        mock_soup = MagicMock()
        mock_beautiful_soup.return_value = mock_soup
        # Instead of using __str__, directly use a string as the content
        mock_soup.select.return_value = ["<div>Selected content</div>"]

        config = WebdownConfig(css_selector="main")
        html_to_markdown("<html><body>Test</body></html>", config)

        # Verify BeautifulSoup was called with the right parameters
        mock_beautiful_soup.assert_called_once_with(
            "<html><body>Test</body></html>", "html.parser"
        )
        mock_soup.select.assert_called_once_with("main")
        # Verify html2text was called with the selected content
        mock_html2text.handle.assert_called_once_with("<div>Selected content</div>")

    def test_table_of_contents(self) -> None:
        """Test table of contents generation."""
        html = "<h1>Title 1</h1><p>Content</p><h2>Title 2</h2><p>More content</p>"

        # Configure html2text to return markdown with headers
        with patch(
            "webdown.markdown_converter.html2text.HTML2Text"
        ) as mock_html2text_class:
            mock_html2text = MagicMock()
            mock_html2text_class.return_value = mock_html2text
            mock_html2text.handle.return_value = (
                "# Title 1\n\nContent\n\n## Title 2\n\nMore content"
            )

            config = WebdownConfig(include_toc=True)
            result = html_to_markdown(html, config)

            # Verify table of contents was generated
            assert "# Table of Contents" in result
            assert "- [Title 1](#title-1)" in result
            assert "  - [Title 2](#title-2)" in result

    def test_compact_output(self) -> None:
        """Test compact output option removes excessive blank lines."""
        html = "<div>Test</div><p>Paragraph</p>"

        with patch(
            "webdown.markdown_converter.html2text.HTML2Text"
        ) as mock_html2text_class:
            mock_html2text = MagicMock()
            mock_html2text_class.return_value = mock_html2text
            # Simulate output with excessive blank lines
            mock_html2text.handle.return_value = "Test\n\n\n\n\nParagraph\n\n\n\nEnd"

            # Without compact option
            config = WebdownConfig(compact_output=False)
            result = html_to_markdown(html, config)
            assert "Test\n\n\n\n\nParagraph\n\n\n\nEnd" in result

            # With compact option
            config = WebdownConfig(compact_output=True)
            result = html_to_markdown(html, config)
            assert "Test\n\nParagraph\n\nEnd" in result

    def test_removes_zero_width_spaces(self) -> None:
        """Test that zero-width spaces are removed from markdown output."""
        html = "<p>Before\u200bAfter</p>"

        with patch(
            "webdown.markdown_converter.html2text.HTML2Text"
        ) as mock_html2text_class:
            mock_html2text = MagicMock()
            mock_html2text_class.return_value = mock_html2text
            # Simulate output with zero-width spaces
            mock_html2text.handle.return_value = "Before\u200bAfter"

            config = WebdownConfig()
            result = html_to_markdown(html, config)
            assert "\u200b" not in result
            assert "BeforeAfter" in result

            # Test multiple invisible characters
            mock_html2text.handle.return_value = (
                "Text with\u200b zero\u200c width\u200d spaces\ufeff!"
            )
            result = html_to_markdown(html, config)
            assert "\u200b" not in result
            assert "\u200c" not in result
            assert "\u200d" not in result
            assert "\ufeff" not in result
            assert "Text with zero width spaces!" in result


class TestConvertUrlToMarkdown:
    """Tests for convert_url_to_markdown function."""

    @patch("webdown.converter.fetch_url")
    @patch("webdown.converter.html_to_markdown")
    def test_conversion_pipeline(
        self, mock_html_to_markdown: MagicMock, mock_fetch_url: MagicMock
    ) -> None:
        """Test that conversion pipeline works correctly."""
        mock_fetch_url.return_value = "<html><body>Test</body></html>"
        mock_html_to_markdown.return_value = "# Test\n\nContent"

        config = WebdownConfig(
            url="https://example.com",
            include_links=True,
            include_images=False,
            include_toc=True,
            css_selector="main",
        )
        result = convert_url_to_markdown(config)

        # Verify fetch_url was called correctly
        mock_fetch_url.assert_called_once_with(
            "https://example.com", show_progress=False
        )

        # Create expected config
        expected_config = WebdownConfig(
            url="https://example.com",
            include_links=True,
            include_images=False,
            include_toc=True,
            css_selector="main",
            compact_output=False,
            body_width=0,
            show_progress=False,
        )

        # Verify html_to_markdown was called with config object as positional arg
        args, kwargs = mock_html_to_markdown.call_args
        assert args[0] == "<html><body>Test</body></html>"  # First arg is HTML
        assert len(args) >= 2  # Should have at least 2 args
        assert args[1].url == expected_config.url
        assert args[1].include_links == expected_config.include_links
        assert args[1].include_images == expected_config.include_images
        assert args[1].include_toc == expected_config.include_toc
        assert args[1].css_selector == expected_config.css_selector
        assert args[1].compact_output == expected_config.compact_output
        assert args[1].body_width == expected_config.body_width

        # Verify result is returned from html_to_markdown
        assert result == "# Test\n\nContent"

    @patch("webdown.converter.fetch_url")
    @patch("webdown.converter.html_to_markdown")
    def test_conversion_with_progress_bar(
        self, mock_html_to_markdown: MagicMock, mock_fetch_url: MagicMock
    ) -> None:
        """Test that conversion pipeline works correctly with progress bar."""
        mock_fetch_url.return_value = "<html><body>Test</body></html>"
        mock_html_to_markdown.return_value = "# Test\n\nContent"

        config = WebdownConfig(
            url="https://example.com",
            show_progress=True,
        )
        result = convert_url_to_markdown(config)

        # Verify fetch_url was called with show_progress=True
        mock_fetch_url.assert_called_once_with(
            "https://example.com", show_progress=True
        )

        # Create expected config
        expected_config = WebdownConfig(
            url="https://example.com",
            include_links=True,
            include_images=True,
            include_toc=False,
            css_selector=None,
            compact_output=False,
            body_width=0,
            show_progress=False,
        )

        # Verify html_to_markdown was called with config object as positional arg
        args, kwargs = mock_html_to_markdown.call_args
        assert args[0] == "<html><body>Test</body></html>"  # First arg is HTML
        assert len(args) >= 2  # Should have at least 2 args
        assert args[1].url == expected_config.url
        assert args[1].include_links == expected_config.include_links
        assert args[1].include_images == expected_config.include_images
        assert args[1].include_toc == expected_config.include_toc
        assert args[1].css_selector == expected_config.css_selector
        assert args[1].compact_output == expected_config.compact_output
        assert args[1].body_width == expected_config.body_width

        # Verify result is returned from html_to_markdown
        assert result == "# Test\n\nContent"

    @patch("webdown.converter.fetch_url")
    @patch("webdown.converter.html_to_markdown")
    def test_conversion_with_custom_body_width(
        self, mock_html_to_markdown: MagicMock, mock_fetch_url: MagicMock
    ) -> None:
        """Test that custom body_width is passed to html_to_markdown."""
        mock_fetch_url.return_value = "<html><body>Test</body></html>"
        mock_html_to_markdown.return_value = "# Test\n\nContent"

        config = WebdownConfig(
            url="https://example.com",
            body_width=80,
        )
        result = convert_url_to_markdown(config)

        # Create expected config
        expected_config = WebdownConfig(
            url="https://example.com",
            include_links=True,
            include_images=True,
            include_toc=False,
            css_selector=None,
            compact_output=False,
            body_width=80,
            show_progress=False,
        )

        # Verify html_to_markdown was called with config object as positional arg
        args, kwargs = mock_html_to_markdown.call_args
        assert args[0] == "<html><body>Test</body></html>"  # First arg is HTML
        assert len(args) >= 2  # Should have at least 2 args
        assert args[1].url == expected_config.url
        assert args[1].include_links == expected_config.include_links
        assert args[1].include_images == expected_config.include_images
        assert args[1].include_toc == expected_config.include_toc
        assert args[1].css_selector == expected_config.css_selector
        assert args[1].compact_output == expected_config.compact_output
        assert args[1].body_width == expected_config.body_width

        # Verify result is returned from html_to_markdown
        assert result == "# Test\n\nContent"

    @patch("webdown.converter.fetch_url")
    @patch("webdown.converter.html_to_markdown")
    def test_conversion_with_config_object(
        self, mock_html_to_markdown: MagicMock, mock_fetch_url: MagicMock
    ) -> None:
        """Test conversion using the WebdownConfig object."""
        mock_fetch_url.return_value = "<html><body>Test</body></html>"
        mock_html_to_markdown.return_value = "# Test\n\nContent"

        # Create config object with custom settings
        config = WebdownConfig(
            url="https://example.com",
            include_toc=True,
            include_images=False,
            body_width=72,
            show_progress=True,
        )

        result = convert_url_to_markdown(config)

        # Verify fetch_url was called with show_progress=True from config
        mock_fetch_url.assert_called_once_with(
            "https://example.com", show_progress=True
        )

        # Verify html_to_markdown was called with config object as positional arg
        args, kwargs = mock_html_to_markdown.call_args
        assert args[0] == "<html><body>Test</body></html>"
        assert args[1] == config

        # Verify result is returned from html_to_markdown
        assert result == "# Test\n\nContent"

    @patch("webdown.html_parser.requests.head")
    @patch("webdown.html_parser.requests.get")
    @patch("webdown.converter.html_to_markdown")
    def test_streaming_mode(
        self,
        mock_html_to_markdown: MagicMock,
        mock_get: MagicMock,
        mock_head: MagicMock,
    ) -> None:
        """Test streaming mode for large documents."""
        # Setup mock HEAD response to trigger streaming (exceeds 10MB threshold)
        mock_head_response = MagicMock()
        mock_head_response.headers = {"content-length": "20000000"}  # 20MB
        mock_head.return_value = mock_head_response

        # Setup mock GET response for streaming
        mock_get_response = MagicMock()
        mock_get_response.headers = {"content-length": "20000000"}
        mock_get_response.iter_content.return_value = [
            b"<html><body>",
            b"<h1>Test</h1>",
            b"<p>Content</p>",
            b"</body></html>",
        ]
        mock_get.return_value = mock_get_response

        # Mock html_to_markdown
        mock_html_to_markdown.return_value = "# Test\n\nContent"

        # Create a config for automated streaming (>10MB)
        config = WebdownConfig(
            url="https://example.com",
            include_toc=True,
        )

        # Call the function
        result = convert_url_to_markdown(config)

        # Verify the result
        assert result == "# Test\n\nContent"

        # Verify HEAD request was made to check size
        mock_head.assert_called_once_with("https://example.com", timeout=5)

        # Verify GET request was made with stream=True
        mock_get.assert_called_once_with("https://example.com", timeout=10, stream=True)

    def test_config_missing_url(self) -> None:
        """Test that WebdownConfig without URL raises an error."""
        # Create config without URL
        config = WebdownConfig(include_toc=True, body_width=80)

        with pytest.raises(WebdownError) as exc_info:
            convert_url_to_markdown(config)

        assert "URL must be provided" in str(exc_info.value)
