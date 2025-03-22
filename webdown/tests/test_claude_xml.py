"""Tests for Claude XML conversion functions."""

from unittest.mock import MagicMock, patch

# pytest imported for decorator but flagged as unused
import pytest  # noqa: F401
import requests_mock

from webdown.converter import (
    ClaudeXMLConfig,
    WebdownConfig,
    convert_url_to_claude_xml,
    markdown_to_claude_xml,
)


class TestMarkdownToClaudeXML:
    """Tests for the markdown_to_claude_xml function."""

    def test_claude_xml_format(self) -> None:
        """Test that Claude XML format is correctly structured."""
        with requests_mock.Mocker() as m:
            # Mock a simple HTML page
            html = """
            <!DOCTYPE html>
            <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Test Heading</h1>
                <p>This is a test paragraph.</p>
                <h2>Subsection</h2>
                <p>Another paragraph with <a href="https://example.com">link</a>.</p>
                <pre><code class="language-python">
                def hello():
                    print("Hello, world!")
                </code></pre>
            </body>
            </html>
            """
            m.get("https://example.com", text=html)
            m.head("https://example.com", headers={"content-length": "500"})

            # Convert to Claude XML
            xml = convert_url_to_claude_xml("https://example.com")

            # Check XML structure
            assert "<claude_documentation>" in xml
            assert "<metadata>" in xml
            assert "<title>Test Heading</title>" in xml
            assert "<source>https://example.com</source>" in xml
            assert "<date>" in xml
            assert "<content>" in xml
            assert "<section>" in xml
            assert "<heading>Test Heading</heading>" in xml
            assert "<text>This is a test paragraph.</text>" in xml
            assert "<heading>Subsection</heading>" in xml
            # The code block is converted to text
            assert "def hello():" in xml
            assert "print(" in xml

    def test_basic_conversion(self) -> None:
        """Test basic conversion of markdown to Claude XML."""
        markdown = "# Test Document\n\nThis is a paragraph."
        xml = markdown_to_claude_xml(markdown, "https://example.com")

        # Check the structure
        assert "<claude_documentation>" in xml
        assert "<metadata>" in xml
        assert "<title>Test Document</title>" in xml
        assert "<source>https://example.com</source>" in xml
        assert "<date>" in xml
        assert "<content>" in xml
        assert "<section>" in xml
        assert "<heading>Test Document</heading>" in xml
        assert "<text>This is a paragraph.</text>" in xml

    def test_code_block_conversion(self) -> None:
        """Test that code blocks are properly converted."""
        markdown = "# Test Document\n\n```python\nprint('Hello, world!')\n```"
        xml = markdown_to_claude_xml(markdown)

        # Check code block is properly formatted
        assert '<code language="python">' in xml
        assert "print('Hello, world!')" in xml
        assert "</code>" in xml

    def test_no_metadata(self) -> None:
        """Test conversion without metadata."""
        markdown = "# Test Document\n\nThis is a paragraph."
        config = ClaudeXMLConfig(include_metadata=False)
        xml = markdown_to_claude_xml(markdown, "https://example.com", config)

        # Metadata should not be present
        assert "<metadata>" not in xml

    def test_no_date(self) -> None:
        """Test conversion without date in metadata."""
        markdown = "# Test Document\n\nThis is a paragraph."
        config = ClaudeXMLConfig(add_date=False)
        xml = markdown_to_claude_xml(markdown, "https://example.com", config)

        # Date should not be present but other metadata should be
        assert "<metadata>" in xml
        assert "<title>" in xml
        assert "<source>" in xml
        assert "<date>" not in xml

    def test_custom_tag_names(self) -> None:
        """Test using custom tag names."""
        markdown = "# Test Document\n\nThis is a paragraph."
        config = ClaudeXMLConfig(doc_tag="custom_doc")
        xml = markdown_to_claude_xml(markdown, config=config)

        # Custom root tag should be used
        assert "<custom_doc>" in xml
        assert "</custom_doc>" in xml

    def test_indented_output(self) -> None:
        """Test output has proper indentation."""
        markdown = "# Test Document\n\nThis is a paragraph."
        xml = markdown_to_claude_xml(markdown)

        # With beautification, there should be indentation
        assert "  <" in xml  # Check for indentation


class TestConvertUrlToClaudeXML:
    """Tests for convert_url_to_claude_xml function."""

    @patch("webdown.converter.convert_url_to_markdown")
    @patch("webdown.converter.markdown_to_claude_xml")
    def test_convert_url_to_claude_xml(
        self, mock_to_xml: MagicMock, mock_to_md: MagicMock
    ) -> None:
        """Test that convert_url_to_claude_xml calls the right functions."""
        # Setup mocks
        mock_to_md.return_value = "# Markdown\n\nContent"
        mock_to_xml.return_value = "<xml>content</xml>"

        # Call the function with a URL
        result = convert_url_to_claude_xml("https://example.com")

        # Verify it called markdown converter with config object internally
        assert mock_to_md.call_count == 1
        # First arg of the first call should be the URL string
        assert mock_to_md.call_args[0][0] == "https://example.com"

        # Verify it called the XML converter with the markdown and URL
        mock_to_xml.assert_called_once_with(
            "# Markdown\n\nContent", "https://example.com", None
        )

        # Verify it returned the XML
        assert result == "<xml>content</xml>"

    @patch("webdown.converter.convert_url_to_markdown")
    @patch("webdown.converter.markdown_to_claude_xml")
    def test_convert_url_to_claude_xml_with_config(
        self, mock_to_xml: MagicMock, mock_to_md: MagicMock
    ) -> None:
        """Test conversion with WebdownConfig and ClaudeXMLConfig."""
        # Setup mocks
        mock_to_md.return_value = "# Markdown\n\nContent"
        mock_to_xml.return_value = "<xml>content</xml>"

        # Create configs
        webdown_config = WebdownConfig(url="https://example.com", include_toc=True)
        claude_config = ClaudeXMLConfig(include_metadata=False)

        # Call the function with configs
        result = convert_url_to_claude_xml(webdown_config, claude_config)

        # Verify it called the markdown converter with the WebdownConfig
        mock_to_md.assert_called_once_with(webdown_config)

        # Verify it called the XML converter with the markdown, URL and ClaudeXMLConfig
        mock_to_xml.assert_called_once_with(
            "# Markdown\n\nContent", "https://example.com", claude_config
        )

        # Verify it returned the XML
        assert result == "<xml>content</xml>"
