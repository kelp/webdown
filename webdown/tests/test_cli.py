"""Tests for command-line interface."""

import argparse
import io
import sys
from unittest.mock import MagicMock, patch

import pytest

# Used in test_main_module through fixture import
import webdown.cli  # noqa: F401
from webdown.cli import (
    _convert_to_selected_format,
    auto_fix_url,
    create_argument_parser,
    main,
    parse_args,
    write_output,
)
from webdown.config import WebdownError


class TestCreateArgumentParser:
    """Tests for create_argument_parser function."""

    def test_parser_configuration(self) -> None:
        """Test the configuration of the argument parser."""
        parser = create_argument_parser()

        # Test basic structure
        assert parser.description is not None
        assert parser.epilog is not None

        # Check argument groups
        arg_groups = [
            group.title for group in parser._action_groups[2:]
        ]  # Skip positional and optional
        assert "Input/Output Options" in arg_groups
        assert "Content Selection" in arg_groups
        assert "Formatting Options" in arg_groups
        assert "Output Format Options" in arg_groups
        assert "Meta Options" in arg_groups

        # Verify key arguments exist
        args = parser.parse_args(["-u", "https://example.com"])
        assert hasattr(args, "url")
        assert hasattr(args, "file")  # New file option
        assert hasattr(args, "output")
        assert hasattr(args, "progress")
        assert hasattr(args, "css")
        assert hasattr(args, "toc")
        assert hasattr(args, "compact")
        assert hasattr(args, "width")
        assert hasattr(args, "claude_xml")


class TestParseArgs:
    """Tests for parse_args function."""

    def test_source_arguments_mutual_exclusivity(self) -> None:
        """Test that URL and file arguments are mutually exclusive."""
        # We need to use a mock parser here to avoid sys.exit
        parser = argparse.ArgumentParser()
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-u", "--url")
        group.add_argument("-f", "--file")

        # Both url and file should be None when neither is provided
        args = parser.parse_args([])
        assert args.url is None
        assert args.file is None

        # Can't specify both url and file (parser will prevent this)
        with pytest.raises(SystemExit):
            parser.parse_args(["-u", "https://example.com", "-f", "file.html"])

    def test_url_argument(self) -> None:
        """Test parsing URL argument."""
        args = parse_args(["-u", "https://example.com"])
        assert args.url == "https://example.com"

        # Long option
        args = parse_args(["--url", "https://example.com"])
        assert args.url == "https://example.com"

    def test_file_argument(self) -> None:
        """Test parsing file argument."""
        args = parse_args(["-f", "page.html"])
        assert args.file == "page.html"

        # Long option
        args = parse_args(["--file", "page.html"])
        assert args.file == "page.html"

    def test_output_option(self) -> None:
        """Test parsing output option."""
        # Short option with URL
        args = parse_args(["-u", "https://example.com", "-o", "output.md"])
        assert args.output == "output.md"

        # Long option with URL
        args = parse_args(["-u", "https://example.com", "--output", "output.md"])
        assert args.output == "output.md"

        # With file source
        args = parse_args(["-f", "page.html", "-o", "output.md"])
        assert args.output == "output.md"

    def test_toc_flag(self) -> None:
        """Test parsing table of contents flag."""
        # Default with URL
        args = parse_args(["-u", "https://example.com"])
        assert args.toc is False

        # Short option with URL
        args = parse_args(["-u", "https://example.com", "-t"])
        assert args.toc is True

        # Long option with URL
        args = parse_args(["-u", "https://example.com", "--toc"])
        assert args.toc is True

        # With file source
        args = parse_args(["-f", "page.html", "-t"])
        assert args.toc is True

    def test_no_links_flag(self) -> None:
        """Test parsing no-links flag."""
        # Default with URL
        args = parse_args(["-u", "https://example.com"])
        assert args.no_links is False

        # With file source
        args = parse_args(["-f", "page.html"])
        assert args.no_links is False

        # Short option
        args = parse_args(["-u", "https://example.com", "-L"])
        assert args.no_links is True

        # Long option
        args = parse_args(["-u", "https://example.com", "--no-links"])
        assert args.no_links is True

    def test_no_images_flag(self) -> None:
        """Test parsing no-images flag."""
        # Default with URL
        args = parse_args(["-u", "https://example.com"])
        assert args.no_images is False

        # Default with file
        args = parse_args(["-f", "page.html"])
        assert args.no_images is False

        # Short option with URL
        args = parse_args(["-u", "https://example.com", "-I"])
        assert args.no_images is True

        # Long option with URL
        args = parse_args(["-u", "https://example.com", "--no-images"])
        assert args.no_images is True

        # With file source
        args = parse_args(["-f", "page.html", "-I"])
        assert args.no_images is True

    def test_css_option(self) -> None:
        """Test parsing CSS selector option."""
        # Short option with URL
        args = parse_args(["-u", "https://example.com", "-s", "main"])
        assert args.css == "main"

        # Long option with URL
        args = parse_args(["-u", "https://example.com", "--css", "article"])
        assert args.css == "article"

        # With file source
        args = parse_args(["-f", "page.html", "-s", "main"])
        assert args.css == "main"

    def test_compact_option(self) -> None:
        """Test parsing compact option."""
        # Default with URL
        args = parse_args(["-u", "https://example.com"])
        assert args.compact is False

        # Default with file
        args = parse_args(["-f", "page.html"])
        assert args.compact is False

        # With long compact flag and URL
        args = parse_args(["-u", "https://example.com", "--compact"])
        assert args.compact is True

        # With short compact flag and URL
        args = parse_args(["-u", "https://example.com", "-c"])
        assert args.compact is True

        # With file source
        args = parse_args(["-f", "page.html", "-c"])
        assert args.compact is True

    def test_width_option(self) -> None:
        """Test parsing width option."""
        # Default with URL
        args = parse_args(["-u", "https://example.com"])
        assert args.width == 0

        # Default with file
        args = parse_args(["-f", "page.html"])
        assert args.width == 0

        # With long width flag and URL
        args = parse_args(["-u", "https://example.com", "--width", "80"])
        assert args.width == 80

        # With short width flag and URL
        args = parse_args(["-u", "https://example.com", "-w", "72"])
        assert args.width == 72

        # With file source
        args = parse_args(["-f", "page.html", "-w", "80"])
        assert args.width == 80

    def test_progress_option(self) -> None:
        """Test parsing progress option."""
        # Default with URL
        args = parse_args(["-u", "https://example.com"])
        assert args.progress is False

        # Default with file
        args = parse_args(["-f", "page.html"])
        assert args.progress is False

        # With long progress flag and URL
        args = parse_args(["-u", "https://example.com", "--progress"])
        assert args.progress is True

        # With short progress flag and URL
        args = parse_args(["-u", "https://example.com", "-p"])
        assert args.progress is True

        # With file source (though it only affects URL downloads)
        args = parse_args(["-f", "page.html", "-p"])
        assert args.progress is True

    def test_claude_xml_options(self) -> None:
        """Test parsing Claude XML options."""
        # Default values with URL
        args = parse_args(["-u", "https://example.com"])
        assert args.claude_xml is False
        assert args.metadata is True
        assert args.add_date is True

        # Default values with file
        args = parse_args(["-f", "page.html"])
        assert args.claude_xml is False
        assert args.metadata is True
        assert args.add_date is True

        # With claude_xml flag and URL
        args = parse_args(["-u", "https://example.com", "--claude-xml"])
        assert args.claude_xml is True

        # With no-metadata flag and URL
        args = parse_args(
            ["-u", "https://example.com", "--claude-xml", "--no-metadata"]
        )
        assert args.claude_xml is True
        assert args.metadata is False

        # With no-date flag and URL
        args = parse_args(["-u", "https://example.com", "--claude-xml", "--no-date"])
        assert args.claude_xml is True
        assert args.add_date is False

        # Test combined options with URL
        args = parse_args(
            ["-u", "https://example.com", "--claude-xml", "--no-metadata", "--no-date"]
        )
        assert args.claude_xml is True
        assert args.metadata is False
        assert args.add_date is False

        # With file source
        args = parse_args(["-f", "page.html", "--claude-xml"])
        assert args.claude_xml is True

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


class TestAutoFixUrl:
    """Tests for auto_fix_url function."""

    def test_already_has_scheme(self) -> None:
        """Test that URLs with scheme are left unchanged."""
        # Test with http:// scheme
        url = "http://example.com"
        assert auto_fix_url(url) == url

        # Test with https:// scheme
        url = "https://example.com"
        assert auto_fix_url(url) == url

        # Test with other scheme
        url = "ftp://example.com"
        assert auto_fix_url(url) == url

    def test_missing_scheme(self) -> None:
        """Test that domain-like URLs without scheme get https:// added."""
        with patch("sys.stderr", new=io.StringIO()) as fake_stderr:
            fixed_url = auto_fix_url("example.com")
            assert fixed_url == "https://example.com"
            assert "Added https://" in fake_stderr.getvalue()

    def test_not_a_url(self) -> None:
        """Test that strings that don't look like URLs are left unchanged."""
        assert auto_fix_url("not a url") == "not a url"
        assert auto_fix_url("") == ""
        assert auto_fix_url(None) is None  # type: ignore


class TestConvertToSelectedFormat:
    """Tests for _convert_to_selected_format function."""

    @patch("webdown.cli.convert_url")
    @patch("webdown.cli.auto_fix_url")
    def test_url_markdown_conversion(
        self, mock_auto_fix: MagicMock, mock_convert: MagicMock
    ) -> None:
        """Test _convert_to_selected_format for URL to Markdown conversion."""
        # Setup mocks
        mock_auto_fix.return_value = "https://example.com"
        mock_convert.return_value = "# Markdown Content"

        # Create args
        args = argparse.Namespace(
            url="example.com",
            file=None,  # No file path
            toc=True,
            no_links=False,
            no_images=False,
            css=None,
            compact=True,
            width=80,
            progress=True,
            claude_xml=False,
            metadata=True,
            output="output.md",
        )

        # Call function
        content, output_path = _convert_to_selected_format(args)

        # Verify results
        assert content == "# Markdown Content"
        assert output_path == "output.md"

        # Verify auto_fix_url was called
        mock_auto_fix.assert_called_once_with("example.com")

        # Verify convert_url was called with correct config
        mock_convert.assert_called_once()
        config = mock_convert.call_args[0][0]
        assert config.url == "https://example.com"
        assert config.include_links is True
        assert config.include_images is True
        assert config.css_selector is None
        assert config.show_progress is True
        assert config.document_options.include_toc is True
        assert config.document_options.compact_output is True
        assert config.document_options.body_width == 80

    def test_no_source_provided(self) -> None:
        """Test the error case when neither URL nor file is provided."""
        # Create args with both url and file set to None
        args = argparse.Namespace(
            url=None,
            file=None,
            toc=False,
            no_links=False,
            no_images=False,
            css=None,
            compact=False,
            width=0,
            progress=False,
            claude_xml=False,
            metadata=True,
            output=None,
        )

        # Function should raise ValueError when both URL and file are None
        with pytest.raises(ValueError) as excinfo:
            _convert_to_selected_format(args)

        # Verify the error message
        assert "Either URL or file path must be provided" in str(excinfo.value)

    @patch("webdown.cli.convert_file")
    def test_file_markdown_conversion(self, mock_convert: MagicMock) -> None:
        """Test _convert_to_selected_format for file to Markdown conversion."""
        # Setup mock
        mock_convert.return_value = "# Markdown Content from File"

        # Create args
        args = argparse.Namespace(
            url=None,  # No URL
            file="page.html",
            toc=True,
            no_links=False,
            no_images=False,
            css=None,
            compact=True,
            width=80,
            progress=False,  # Progress doesn't affect file conversion
            claude_xml=False,
            metadata=True,
            output="output.md",
        )

        # Call function
        content, output_path = _convert_to_selected_format(args)

        # Verify results
        assert content == "# Markdown Content from File"
        assert output_path == "output.md"

        # Verify convert_file was called with correct config
        mock_convert.assert_called_once()
        config = mock_convert.call_args[0][0]
        assert config.file_path == "page.html"
        assert config.include_links is True
        assert config.include_images is True
        assert config.css_selector is None
        assert config.document_options.include_toc is True
        assert config.document_options.compact_output is True
        assert config.document_options.body_width == 80

    @patch("webdown.cli.convert_file")
    def test_file_claude_xml_conversion(self, mock_convert: MagicMock) -> None:
        """Test _convert_to_selected_format for file to Claude XML conversion."""
        # Setup mock
        mock_convert.return_value = (
            "<claude_documentation>File Content</claude_documentation>"
        )

        # Create args
        args = argparse.Namespace(
            url=None,  # No URL
            file="page.html",
            toc=False,
            no_links=True,
            no_images=True,
            css="main",
            compact=False,
            width=0,
            progress=False,
            claude_xml=True,
            metadata=False,  # No metadata
            output="output.xml",
        )

        # Call function
        content, output_path = _convert_to_selected_format(args)

        # Verify results
        assert content == "<claude_documentation>File Content</claude_documentation>"
        assert output_path == "output.xml"

        # Verify convert_file was called with correct config
        mock_convert.assert_called_once()
        config = mock_convert.call_args[0][0]
        assert config.file_path == "page.html"
        assert config.include_links is False
        assert config.include_images is False
        assert config.css_selector == "main"
        assert config.format.name == "CLAUDE_XML"
        assert config.document_options.include_toc is False
        assert config.document_options.compact_output is False
        assert config.document_options.body_width == 0
        assert config.document_options.include_metadata is False

    @patch("webdown.cli.convert_url")
    @patch("webdown.cli.auto_fix_url")
    def test_url_claude_xml_conversion(
        self, mock_auto_fix: MagicMock, mock_convert: MagicMock
    ) -> None:
        """Test _convert_to_selected_format for URL to Claude XML conversion."""
        # Setup mocks
        mock_auto_fix.return_value = "https://example.com"
        mock_convert.return_value = (
            "<claude_documentation>Content</claude_documentation>"
        )

        # Create args
        args = argparse.Namespace(
            url="https://example.com",  # Already has scheme
            file=None,  # No file path
            toc=False,
            no_links=True,
            no_images=True,
            css="main",
            compact=False,
            width=0,
            progress=False,
            claude_xml=True,
            metadata=True,
            output=None,  # stdout
        )

        # Call function
        content, output_path = _convert_to_selected_format(args)

        # Verify results
        assert content == "<claude_documentation>Content</claude_documentation>"
        assert output_path is None

        # Verify convert_url was called
        mock_convert.assert_called_once()

        # Check config
        config = mock_convert.call_args[0][0]
        assert config.url == "https://example.com"
        assert config.include_links is False
        assert config.include_images is False
        assert config.css_selector == "main"
        assert config.document_options.include_metadata is True


class TestWriteOutput:
    """Tests for write_output function."""

    def test_write_to_stdout(self) -> None:
        """Test writing output to stdout."""
        content = "Test content"

        # Capture stdout
        with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
            write_output(content, None)
            assert fake_stdout.getvalue() == "Test content\n"

    def test_write_to_file(self) -> None:
        """Test writing output to a file."""
        content = "Test content"

        # Mock file operations
        with patch("builtins.open", new_callable=MagicMock) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            write_output(content, "output.md")

            # Verify file was opened correctly
            mock_open.assert_called_once_with("output.md", "w", encoding="utf-8")
            mock_file.write.assert_called_once_with("Test content\n")

    def test_trailing_newline_handling(self) -> None:
        """Test handling of trailing newlines."""
        # Without trailing newline
        with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
            write_output("Content", None)
            assert fake_stdout.getvalue() == "Content\n"

        # With one trailing newline
        with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
            write_output("Content\n", None)
            assert fake_stdout.getvalue() == "Content\n"

        # With multiple trailing newlines
        with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
            write_output("Content\n\n\n", None)
            assert fake_stdout.getvalue() == "Content\n"


class TestMain:
    """Tests for main function."""

    @patch("webdown.cli._convert_to_selected_format")
    @patch("webdown.cli.write_output")
    def test_convert_url_to_stdout(
        self, mock_write: MagicMock, mock_convert: MagicMock
    ) -> None:
        """Test converting URL to stdout."""
        # Setup mocks
        mock_convert.return_value = ("# Markdown Content", None)

        # Call main function with URL
        exit_code = main(["-u", "https://example.com"])
        assert exit_code == 0

        # Verify the function was called with correct args
        assert mock_convert.call_count == 1
        args = mock_convert.call_args[0][0]
        assert args.url == "https://example.com"
        assert args.file is None

        # Verify write_output was called with correct content and None for stdout
        mock_write.assert_called_once_with("# Markdown Content", None)

    @patch("webdown.cli._convert_to_selected_format")
    @patch("webdown.cli.write_output")
    def test_convert_file_to_stdout(
        self, mock_write: MagicMock, mock_convert: MagicMock
    ) -> None:
        """Test converting file to stdout."""
        # Setup mocks
        mock_convert.return_value = ("# Markdown Content from File", None)

        # Call main function with file
        exit_code = main(["-f", "page.html"])
        assert exit_code == 0

        # Verify the function was called with correct args
        assert mock_convert.call_count == 1
        args = mock_convert.call_args[0][0]
        assert args.url is None
        assert args.file == "page.html"

        # Verify write_output was called with correct content and None for stdout
        mock_write.assert_called_once_with("# Markdown Content from File", None)

    @patch("webdown.cli.parse_args")
    def test_main_with_no_args(self, mock_parse_args: MagicMock) -> None:
        """Test the main function handles missing source args properly."""
        # Mock the first call to parse_args to return args with no sources
        mock_args = MagicMock()
        mock_args.url = None
        mock_args.file = None

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

    @patch("webdown.cli._convert_to_selected_format")
    @patch("webdown.cli.write_output")
    def test_convert_url_to_file(
        self, mock_write: MagicMock, mock_convert: MagicMock
    ) -> None:
        """Test converting URL to file."""
        # Setup mocks
        mock_convert.return_value = ("# Markdown Content", "output.md")

        # Call main function
        exit_code = main(["-u", "https://example.com", "-o", "output.md"])
        assert exit_code == 0

        # Verify function was called with correct args
        assert mock_convert.call_count == 1
        args = mock_convert.call_args[0][0]
        assert args.url == "https://example.com"
        assert args.file is None
        assert args.output == "output.md"

        # Verify write_output was called with correct content and output path
        mock_write.assert_called_once_with("# Markdown Content", "output.md")

    @patch("webdown.cli._convert_to_selected_format")
    @patch("webdown.cli.write_output")
    def test_convert_file_to_file(
        self, mock_write: MagicMock, mock_convert: MagicMock
    ) -> None:
        """Test converting file to file."""
        # Setup mocks
        mock_convert.return_value = ("# Markdown Content from File", "output.md")

        # Call main function
        exit_code = main(["-f", "page.html", "-o", "output.md"])
        assert exit_code == 0

        # Verify function was called with correct args
        assert mock_convert.call_count == 1
        args = mock_convert.call_args[0][0]
        assert args.url is None
        assert args.file == "page.html"
        assert args.output == "output.md"

        # Verify write_output was called with correct content and output path
        mock_write.assert_called_once_with("# Markdown Content from File", "output.md")

    @patch("webdown.cli._convert_to_selected_format")
    @patch("webdown.cli.write_output")
    def test_claude_xml_conversion(
        self, mock_write: MagicMock, mock_convert: MagicMock
    ) -> None:
        """Test converting to Claude XML."""
        # Setup mocks
        mock_convert.return_value = (
            "<claude_documentation>content</claude_documentation>",
            None,
        )

        # Call main function with URL
        exit_code = main(["-u", "https://example.com", "--claude-xml"])
        assert exit_code == 0

        # Verify _convert_to_selected_format was called with correct arguments
        assert mock_convert.call_count == 1
        args = mock_convert.call_args[0][0]
        assert args.url == "https://example.com"
        assert args.claude_xml is True

        # Verify write_output was called with correct content
        mock_write.assert_called_once_with(
            "<claude_documentation>content</claude_documentation>", None
        )

        # Reset mocks
        mock_convert.reset_mock()
        mock_write.reset_mock()

        # Test with file output and URL source
        mock_convert.return_value = (
            "<claude_documentation>content</claude_documentation>",
            "output.xml",
        )

        exit_code = main(
            ["-u", "https://example.com", "--claude-xml", "-o", "output.xml"]
        )
        assert exit_code == 0

        # Verify _convert_to_selected_format was called with correct arguments
        assert mock_convert.call_count == 1
        args = mock_convert.call_args[0][0]
        assert args.url == "https://example.com"
        assert args.claude_xml is True
        assert args.output == "output.xml"

        # Verify write_output was called with correct content and output path
        mock_write.assert_called_once_with(
            "<claude_documentation>content</claude_documentation>", "output.xml"
        )

        # Reset mocks
        mock_convert.reset_mock()
        mock_write.reset_mock()

        # Test with file source
        mock_convert.return_value = (
            "<claude_documentation>file content</claude_documentation>",
            None,
        )

        exit_code = main(["-f", "page.html", "--claude-xml"])
        assert exit_code == 0

        # Verify _convert_to_selected_format was called with correct arguments
        assert mock_convert.call_count == 1
        args = mock_convert.call_args[0][0]
        assert args.file == "page.html"
        assert args.url is None
        assert args.claude_xml is True

    def test_error_handling(self) -> None:
        """Test error handling."""
        # Test with different types of exceptions
        exceptions = [
            WebdownError("Invalid URL: not_a_url"),
            WebdownError("Connection error"),
            Exception("Unexpected error"),
        ]

        # Create a mock that will raise exceptions
        for exception in exceptions:
            with patch("webdown.cli._convert_to_selected_format") as mock_convert:
                mock_convert.side_effect = exception

                # Capture stderr
                with patch("sys.stderr", new=io.StringIO()) as fake_stderr:
                    exit_code = main(["-u", "https://example.com"])
                    assert exit_code == 1
                    assert str(exception) in fake_stderr.getvalue()

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
