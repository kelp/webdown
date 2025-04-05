"""Integration tests for webdown."""

import os
import tempfile

import requests_mock

from webdown.cli import main
from webdown.config import DocumentOptions, OutputFormat
from webdown.converter import WebdownConfig, convert_url

# Sample HTML content for testing
SAMPLE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Test Page</title>
</head>
<body>
    <header>
        <h1>Test Page Title</h1>
    </header>
    <main>
        <h2>Section 1</h2>
        <p>This is a paragraph with a <a href="https://example.com">link</a>.</p>
        <h2>Section 2</h2>
        <p>This is another paragraph with an
           <img src="https://example.com/image.jpg" alt="image">.</p>
    </main>
</body>
</html>"""


class TestIntegration:
    """Integration tests for webdown."""

    def test_convert_with_requests_mock(self) -> None:
        """Test conversion with mocked HTTP requests."""
        with requests_mock.Mocker() as m:
            m.get("https://example.com", text=SAMPLE_HTML)
            # Mock the HEAD request to simulate a content-length response
            m.head("https://example.com", headers={"content-length": "5000"})

            # Basic conversion
            config = WebdownConfig(
                url="https://example.com", format=OutputFormat.MARKDOWN
            )
            result = convert_url(config)
            assert "# Test Page Title" in result
            assert "## Section 1" in result
            assert "link" in result
            assert "image" in result

            # With no links
            config = WebdownConfig(
                url="https://example.com",
                include_links=False,
                format=OutputFormat.MARKDOWN,
            )
            result = convert_url(config)
            assert "# Test Page Title" in result
            assert (
                "[link](https://example.com)" not in result
            )  # Link should be plain text, not hyperlink

            # With no images
            config = WebdownConfig(
                url="https://example.com",
                include_images=False,
                format=OutputFormat.MARKDOWN,
            )
            result = convert_url(config)
            assert "# Test Page Title" in result
            assert "image.jpg" not in result

            # With CSS selector
            config = WebdownConfig(
                url="https://example.com",
                css_selector="main",
                format=OutputFormat.MARKDOWN,
            )
            result = convert_url(config)
            assert "Test Page Title" not in result  # Header is outside <main>
            assert "## Section 1" in result
            assert "## Section 2" in result

            # With table of contents
            config = WebdownConfig(
                url="https://example.com",
                format=OutputFormat.MARKDOWN,
                document_options=DocumentOptions(include_toc=True),
            )
            result = convert_url(config)
            assert "# Table of Contents" in result
            assert "- [Test Page Title](#test-page-title)" in result
            assert "  - [Section 1](#section-1)" in result
            assert "  - [Section 2](#section-2)" in result

    def test_cli_to_file(self) -> None:
        """Test CLI writing to file."""
        with requests_mock.Mocker() as m:
            m.get("https://example.com", text=SAMPLE_HTML)
            # Mock the HEAD request to simulate a content-length response
            m.head("https://example.com", headers={"content-length": "5000"})

            with tempfile.TemporaryDirectory() as tmp_dir:
                output_file = os.path.join(tmp_dir, "output.md")

                # Run CLI with output to file (using new -u/--url flag)
                exit_code = main(["-u", "https://example.com", "-o", output_file])
                assert exit_code == 0

                # Check file exists and contains expected content
                assert os.path.exists(output_file)
                with open(output_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    assert "# Test Page Title" in content
                    assert "## Section 1" in content
                    assert "## Section 2" in content

    def test_cli_file_to_file(self) -> None:
        """Test CLI converting local HTML file to markdown file."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create a temporary HTML file with the sample content
            input_file = os.path.join(tmp_dir, "input.html")
            with open(input_file, "w", encoding="utf-8") as f:
                f.write(SAMPLE_HTML)

            # Create output path
            output_file = os.path.join(tmp_dir, "output.md")

            # Run CLI with file input and output
            exit_code = main(["-f", input_file, "-o", output_file])
            assert exit_code == 0

            # Check file exists and contains expected content
            assert os.path.exists(output_file)
            with open(output_file, "r", encoding="utf-8") as f:
                content = f.read()
                assert "# Test Page Title" in content
                assert "## Section 1" in content
                assert "## Section 2" in content
