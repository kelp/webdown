"""Tests for command-line interface."""

import io
import sys
from unittest.mock import MagicMock, patch

import pytest

from webdown.cli import main, parse_args
from webdown.converter import InvalidURLError, NetworkError


class TestParseArgs:
    """Tests for parse_args function."""

    def test_required_url_argument(self) -> None:
        """Test that URL argument is required."""
        with pytest.raises(SystemExit):
            parse_args([])

    def test_url_argument(self) -> None:
        """Test parsing URL argument."""
        args = parse_args(["https://example.com"])
        assert args.url == "https://example.com"

    def test_output_option(self) -> None:
        """Test parsing output option."""
        # Short option
        args = parse_args(["https://example.com", "-o", "output.md"])
        assert args.output == "output.md"

        # Long option
        args = parse_args(["https://example.com", "--output", "output.md"])
        assert args.output == "output.md"

    def test_toc_flag(self) -> None:
        """Test parsing table of contents flag."""
        # Default
        args = parse_args(["https://example.com"])
        assert args.toc is False

        # Short option
        args = parse_args(["https://example.com", "-t"])
        assert args.toc is True

        # Long option
        args = parse_args(["https://example.com", "--toc"])
        assert args.toc is True

    def test_no_links_flag(self) -> None:
        """Test parsing no-links flag."""
        # Default
        args = parse_args(["https://example.com"])
        assert args.no_links is False

        # Short option
        args = parse_args(["https://example.com", "-L"])
        assert args.no_links is True

        # Long option
        args = parse_args(["https://example.com", "--no-links"])
        assert args.no_links is True

    def test_no_images_flag(self) -> None:
        """Test parsing no-images flag."""
        # Default
        args = parse_args(["https://example.com"])
        assert args.no_images is False

        # Short option
        args = parse_args(["https://example.com", "-I"])
        assert args.no_images is True

        # Long option
        args = parse_args(["https://example.com", "--no-images"])
        assert args.no_images is True

    def test_css_option(self) -> None:
        """Test parsing CSS selector option."""
        # Short option
        args = parse_args(["https://example.com", "-c", "main"])
        assert args.css == "main"

        # Long option
        args = parse_args(["https://example.com", "--css", "article"])
        assert args.css == "article"


class TestMain:
    """Tests for main function."""

    @patch("webdown.cli.convert_url_to_markdown")
    def test_convert_to_stdout(self, mock_convert: MagicMock) -> None:
        """Test converting URL to stdout."""
        mock_convert.return_value = "# Markdown Content"

        # Redirect stdout for testing
        stdout_backup = sys.stdout
        try:
            out = io.StringIO()
            sys.stdout = out
            exit_code = main(["https://example.com"])
            assert exit_code == 0
            assert out.getvalue() == "# Markdown Content"
        finally:
            sys.stdout = stdout_backup

        # Verify convert_url_to_markdown was called with correct parameters
        mock_convert.assert_called_once_with(
            "https://example.com",
            include_toc=False,
            include_links=True,
            include_images=True,
            css_selector=None,
        )

    @patch("webdown.cli.convert_url_to_markdown")
    @patch("builtins.open", new_callable=MagicMock)
    def test_convert_to_file(
        self, mock_open: MagicMock, mock_convert: MagicMock
    ) -> None:
        """Test converting URL to file."""
        mock_convert.return_value = "# Markdown Content"
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        exit_code = main(["https://example.com", "-o", "output.md"])
        assert exit_code == 0

        # Verify file was opened and written to
        mock_open.assert_called_once_with("output.md", "w", encoding="utf-8")
        mock_file.write.assert_called_once_with("# Markdown Content")

    @patch("webdown.cli.convert_url_to_markdown")
    def test_error_handling(self, mock_convert: MagicMock) -> None:
        """Test error handling."""
        # Test InvalidURLError
        mock_convert.side_effect = InvalidURLError("Invalid URL: not_a_url")

        stderr_backup = sys.stderr
        try:
            err = io.StringIO()
            sys.stderr = err
            exit_code = main(["not_a_url"])
            assert exit_code == 1
            assert "Invalid URL: not_a_url" in err.getvalue()
        finally:
            sys.stderr = stderr_backup

        # Test NetworkError
        mock_convert.side_effect = NetworkError("Connection error")

        try:
            err = io.StringIO()
            sys.stderr = err
            exit_code = main(["https://example.com"])
            assert exit_code == 1
            assert "Connection error" in err.getvalue()
        finally:
            sys.stderr = stderr_backup

        # Test generic exception
        mock_convert.side_effect = Exception("Unexpected error")

        try:
            err = io.StringIO()
            sys.stderr = err
            exit_code = main(["https://example.com"])
            assert exit_code == 1
            assert "Unexpected error" in err.getvalue()
        finally:
            sys.stderr = stderr_backup
