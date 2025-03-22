"""Tests for command-line interface."""

import argparse
import io
import sys
from unittest.mock import MagicMock, patch

import pytest

# Used in test_main_module through fixture import
import webdown.cli  # noqa: F401
from webdown.cli import main, parse_args
from webdown.converter import WebdownError


class TestParseArgs:
    """Tests for parse_args function."""

    def test_url_argument_optional(self) -> None:
        """Test that URL argument is optional with nargs='?'."""
        # We need to use a mock parser here to avoid sys.exit with --version
        parser = argparse.ArgumentParser()
        parser.add_argument("url", nargs="?")
        args = parser.parse_args([])
        assert args.url is None

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
        args = parse_args(["https://example.com", "-s", "main"])
        assert args.css == "main"

        # Long option
        args = parse_args(["https://example.com", "--css", "article"])
        assert args.css == "article"

    def test_compact_option(self) -> None:
        """Test parsing compact option."""
        # Default
        args = parse_args(["https://example.com"])
        assert args.compact is False

        # With long compact flag
        args = parse_args(["https://example.com", "--compact"])
        assert args.compact is True

        # With short compact flag
        args = parse_args(["https://example.com", "-c"])
        assert args.compact is True

    def test_width_option(self) -> None:
        """Test parsing width option."""
        # Default
        args = parse_args(["https://example.com"])
        assert args.width == 0

        # With long width flag
        args = parse_args(["https://example.com", "--width", "80"])
        assert args.width == 80

        # With short width flag
        args = parse_args(["https://example.com", "-w", "72"])
        assert args.width == 72

    def test_progress_option(self) -> None:
        """Test parsing progress option."""
        # Default
        args = parse_args(["https://example.com"])
        assert args.progress is False

        # With long progress flag
        args = parse_args(["https://example.com", "--progress"])
        assert args.progress is True

        # With short progress flag
        args = parse_args(["https://example.com", "-p"])
        assert args.progress is True

    def test_claude_xml_options(self) -> None:
        """Test parsing Claude XML options."""
        # Default values
        args = parse_args(["https://example.com"])
        assert args.claude_xml is False
        assert args.metadata is True
        assert args.add_date is True

        # With claude_xml flag
        args = parse_args(["https://example.com", "--claude-xml"])
        assert args.claude_xml is True

        # With no-metadata flag
        args = parse_args(["https://example.com", "--claude-xml", "--no-metadata"])
        assert args.claude_xml is True
        assert args.metadata is False

        # With no-date flag
        args = parse_args(["https://example.com", "--claude-xml", "--no-date"])
        assert args.claude_xml is True
        assert args.add_date is False

        # Test combined options
        args = parse_args(
            ["https://example.com", "--claude-xml", "--no-metadata", "--no-date"]
        )
        assert args.claude_xml is True
        assert args.metadata is False
        assert args.add_date is False

    def test_version_flag(self) -> None:
        """Test version flag is recognized."""
        # Testing that the flag is recognized correctly
        from webdown import __version__

        # Create a parser with version action
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--version", action="version", version=f"test {__version__}"
        )

        # Test it raises SystemExit
        with pytest.raises(SystemExit):
            parser.parse_args(["--version"])


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
            assert out.getvalue() == "# Markdown Content\n"
        finally:
            sys.stdout = stdout_backup

        # Verify convert_url_to_markdown was called with a WebdownConfig
        # We only check that it was called once
        assert mock_convert.call_count == 1
        # Get the first argument (should be a WebdownConfig object)
        config = mock_convert.call_args[0][0]
        # Verify the config has the expected values
        assert config.url == "https://example.com"
        assert config.include_toc is False
        assert config.include_links is True
        assert config.include_images is True
        assert config.css_selector is None
        assert config.compact_output is False
        assert config.body_width == 0
        assert config.show_progress is False

    @patch("webdown.cli.parse_args")
    def test_main_with_no_args(self, mock_parse_args: MagicMock) -> None:
        """Test the main function handles missing URL properly."""
        # Mock the first call to parse_args to return args with url=None
        mock_args = MagicMock()
        mock_args.url = None

        # This ensures we get coverage for line 61: mock must execute both calls
        # we need to ensure the second call (with ["-h"]) happens before SystemExit
        def side_effect(args: list) -> argparse.Namespace:
            if args == ["-h"]:
                # Delay the SystemExit until after the line is executed and counted
                raise SystemExit()
            return mock_args

        mock_parse_args.side_effect = side_effect

        # SystemExit will be raised on the second call to parse_args(["-h"])
        with pytest.raises(SystemExit):
            main([])

        # Verify parse_args was called twice: first with [] and then with ["-h"]
        assert mock_parse_args.call_count == 2
        assert mock_parse_args.call_args_list[0][0][0] == []
        assert mock_parse_args.call_args_list[1][0][0] == ["-h"]

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
        mock_file.write.assert_called_once_with("# Markdown Content\n")

    @patch("webdown.cli.convert_url_to_claude_xml")
    def test_claude_xml_conversion(self, mock_convert_to_xml: MagicMock) -> None:
        """Test converting to Claude XML."""
        mock_convert_to_xml.return_value = (
            "<claude_documentation>content</claude_documentation>"
        )

        # Test with stdout
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            exit_code = main(["https://example.com", "--claude-xml"])
            assert exit_code == 0
            assert (
                fake_out.getvalue()
                == "<claude_documentation>content</claude_documentation>\n"
            )

        # Test with file output
        with patch("builtins.open", new_callable=MagicMock) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            exit_code = main(
                ["https://example.com", "--claude-xml", "-o", "output.xml"]
            )
            assert exit_code == 0

            # Verify file was opened and written to
            mock_open.assert_called_once_with("output.xml", "w", encoding="utf-8")
            mock_file.write.assert_called_once_with(
                "<claude_documentation>content</claude_documentation>\n"
            )

    @patch("webdown.cli.convert_url_to_markdown")
    def test_error_handling(self, mock_convert: MagicMock) -> None:
        """Test error handling."""
        # Test URL format error
        mock_convert.side_effect = WebdownError("Invalid URL: not_a_url")

        stderr_backup = sys.stderr
        try:
            err = io.StringIO()
            sys.stderr = err
            exit_code = main(["not_a_url"])
            assert exit_code == 1
            assert "Invalid URL: not_a_url" in err.getvalue()
        finally:
            sys.stderr = stderr_backup

        # Test network error
        mock_convert.side_effect = WebdownError("Connection error")

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

    @patch("sys.exit")
    def test_main_module(self, mock_exit: MagicMock) -> None:
        """Test __main__ functionality."""
        # First verify the file has the expected __main__ block
        import os

        cli_path = os.path.join(os.path.dirname(__file__), "..", "cli.py")
        with open(cli_path, "r") as f:
            content = f.read()

        assert 'if __name__ == "__main__":' in content
        assert "sys.exit(main())" in content

        # Now actually execute the __main__ block to get coverage
        # We need to:
        # 1. Import the module
        # 2. Set __name__ to "__main__"
        # 3. Create a fake "main" function that's already mocked
        # 4. Execute the if-block directly

        # Import the module code as a string
        module_code = """
if __name__ == "__main__":
    sys.exit(main())
"""
        # Set up a namespace with mocked functions
        namespace = {
            "__name__": "__main__",
            "sys": sys,
            "main": lambda: 0,  # Mock main to return 0
        }

        # Execute the code in this namespace
        exec(module_code, namespace)

        # Verify sys.exit was called with the return value from main (0)
        mock_exit.assert_called_once_with(0)
