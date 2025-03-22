"""Tests for configuration parameter combinations."""

import pytest
import requests_mock

from webdown.config import DocumentOptions, OutputFormat, WebdownConfig
from webdown.converter import convert_url


class TestConfigCombinations:
    """Tests for various combinations of configuration parameters."""

    @pytest.fixture  # type: ignore
    def mock_response(self) -> str:
        """Sample HTML content for testing."""
        return """<!DOCTYPE html>
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
                <p>This is a paragraph with a <a href="https://example.com">link</a></p>
                <h2>Section 2</h2>
                <p>This is another paragraph with an
                  <img src="https://example.com/image.jpg" alt="image">.</p>
                <pre><code class="language-python">
                print("Hello World")
                </code></pre>
            </main>
        </body>
        </html>"""

    def test_basic_configs(self, mock_response: str) -> None:
        """Test basic configuration combinations."""
        url = "https://example.com"

        with requests_mock.Mocker() as m:
            m.get(url, text=mock_response)
            m.head(url, headers={"content-length": "5000"})

            # Test default config
            config = WebdownConfig(url=url)
            result = convert_url(config)
            assert "# Test Page Title" in result
            assert "[link](https://example.com)" in result
            assert "image.jpg" in result

            # Test with both links and images disabled
            config = WebdownConfig(url=url, include_links=False, include_images=False)
            result = convert_url(config)
            assert "# Test Page Title" in result
            assert "[link](https://example.com)" not in result
            assert "link" in result  # Text should still be there
            assert "image.jpg" not in result

    def test_document_options_combinations(self, mock_response: str) -> None:
        """Test combinations of document options."""
        url = "https://example.com"

        with requests_mock.Mocker() as m:
            m.get(url, text=mock_response)
            m.head(url, headers={"content-length": "5000"})

            # Test with TOC
            doc_options = DocumentOptions(include_toc=True)
            config = WebdownConfig(url=url, document_options=doc_options)
            result = convert_url(config)
            assert "# Table of Contents" in result
            assert "- [Test Page Title](#test-page-title)" in result

            # Test with compact output
            doc_options = DocumentOptions(compact_output=True)
            config = WebdownConfig(url=url, document_options=doc_options)
            result = convert_url(config)
            # Compact output would remove excessive blank lines
            # This is hard to test directly, but we can ensure content is still there
            assert "# Test Page Title" in result

            # Test with custom body width
            doc_options = DocumentOptions(body_width=40)
            config = WebdownConfig(url=url, document_options=doc_options)
            result = convert_url(config)
            assert "# Test Page Title" in result
            # Body width affects line wrapping which is hard to test directly

    def test_output_format_combinations(self, mock_response: str) -> None:
        """Test different output formats."""
        url = "https://example.com"

        with requests_mock.Mocker() as m:
            m.get(url, text=mock_response)
            m.head(url, headers={"content-length": "5000"})

            # Test markdown format
            config = WebdownConfig(url=url, format=OutputFormat.MARKDOWN)
            result = convert_url(config)
            assert "# Test Page Title" in result
            assert "<claude_documentation>" not in result

            # Test Claude XML format
            config = WebdownConfig(url=url, format=OutputFormat.CLAUDE_XML)
            result = convert_url(config)
            assert "<claude_documentation>" in result
            assert "</claude_documentation>" in result
            assert "<source>https://example.com</source>" in result

            # Test Claude XML without metadata
            doc_options = DocumentOptions(include_metadata=False)
            config = WebdownConfig(
                url=url, format=OutputFormat.CLAUDE_XML, document_options=doc_options
            )
            result = convert_url(config)
            assert "<claude_documentation>" in result
            assert "<metadata>" not in result

    def test_css_selector_with_options(self, mock_response: str) -> None:
        """Test CSS selector combined with other options."""
        url = "https://example.com"

        with requests_mock.Mocker() as m:
            m.get(url, text=mock_response)
            m.head(url, headers={"content-length": "5000"})

            # CSS selector with TOC
            doc_options = DocumentOptions(include_toc=True)
            config = WebdownConfig(
                url=url, css_selector="main", document_options=doc_options
            )
            result = convert_url(config)
            assert "# Table of Contents" in result
            assert "Test Page Title" not in result  # Outside the main tag
            assert "- [Section 1](#section-1)" in result
            assert "- [Section 2](#section-2)" in result

            # CSS selector with XML output
            config = WebdownConfig(
                url=url, css_selector="main", format=OutputFormat.CLAUDE_XML
            )
            result = convert_url(config)
            assert "<claude_documentation>" in result
            assert "Test Page Title" not in result  # Outside the main tag
            assert "Section 1" in result
            assert "Section 2" in result
