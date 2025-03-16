"""Tests for the WebdownConfig functionality."""

import pytest
import requests_mock

from webdown.converter import (
    WebdownConfig,
    WebdownError,
    convert_url_to_markdown,
    html_to_markdown,
)

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


class TestWebdownConfig:
    """Tests for the WebdownConfig class and its usage in converter functions."""

    def test_html_to_markdown_with_config(self) -> None:
        """Test html_to_markdown with WebdownConfig object."""
        # Create config with various options
        config = WebdownConfig(
            include_links=False,
            include_images=False,
            include_toc=True,
            compact_output=True,
            body_width=80,
            single_line_break=True,
            protect_links=True,
            images_as_html=True,
            unicode_snob=True,
            tables_as_html=True,
            emphasis_mark="*",  # Changed from "-" to avoid conflict with list items
            strong_mark="__",
            default_image_alt="No image description",
            pad_tables=True,
            wrap_list_items=True,
        )

        # Convert HTML to Markdown using config
        markdown = html_to_markdown(SAMPLE_HTML, config=config)

        # Verify the config options were applied
        assert "# Test Page Title" in markdown
        assert "## Section 1" in markdown
        assert "## Section 2" in markdown
        assert "# Table of Contents" in markdown
        assert "[link](https://example.com)" not in markdown  # Links should be ignored
        assert "![image]" not in markdown  # Images should be ignored

    def test_convert_url_to_markdown_with_config(self) -> None:
        """Test convert_url_to_markdown with WebdownConfig object."""
        with requests_mock.Mocker() as m:
            # Use our sample HTML
            m.get("https://example.com", text=SAMPLE_HTML)
            m.head("https://example.com", headers={"content-length": "500"})

            # Create config object focusing on configuration options we want to test
            config = WebdownConfig(
                url="https://example.com",
                include_links=False,  # Should remove links
                include_images=False,  # Should remove images
                body_width=80,  # Set specific body width
                show_progress=True,
            )

            # Convert using config object
            markdown = convert_url_to_markdown(config)

            # No link brackets should be present since include_links=False
            assert "[link]" not in markdown
            assert "link" in markdown  # But the text should be there

            # No image syntax should be present since include_images=False
            assert "![" not in markdown

            # Let's also test that we're using the config object correctly
            import unittest.mock

            # Use mock to verify converter functions use the config as expected
            with unittest.mock.patch(
                "webdown.converter.html_to_markdown"
            ) as mock_html_to_md:
                convert_url_to_markdown(config)
                # Verify html_to_markdown was called with our config object
                assert mock_html_to_md.call_args[1]["config"] == config

    def test_convert_url_with_missing_url(self) -> None:
        """Test error when URL is missing from config."""
        config = WebdownConfig()  # No URL provided

        with pytest.raises(WebdownError) as excinfo:
            convert_url_to_markdown(config)

        assert "URL must be provided" in str(excinfo.value)
