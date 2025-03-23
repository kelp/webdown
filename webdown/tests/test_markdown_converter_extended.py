"""Extended tests for markdown converter to improve coverage."""

import pytest

from webdown.config import WebdownConfig, WebdownError
from webdown.markdown_converter import (
    _create_toc_link,
    _find_code_blocks,
    _extract_headings,
    _is_position_in_code_block,
    _validate_body_width,
    generate_table_of_contents,
    html_to_markdown,
)


class TestCodeBlocks:
    """Tests for code block handling."""

    def test_extract_code_blocks(self):
        """Test extracting code blocks from markdown."""
        # Sample markdown with code blocks
        markdown = """
# Title

```python
def hello():
    print("Hello, world!")
```

Some text

```
Plain code block
```
"""
        blocks = _find_code_blocks(markdown)
        assert len(blocks) == 2
        
        # Extract the actual code blocks to verify
        block1 = markdown[blocks[0][0]:blocks[0][1]]
        block2 = markdown[blocks[1][0]:blocks[1][1]]
        
        assert "```python" in block1
        assert "def hello()" in block1
        assert "```" in block2
        assert "Plain code block" in block2


class TestHeadings:
    """Tests for heading extraction."""

    def test_headings_in_code_blocks(self):
        """Test that headings inside code blocks are ignored."""
        markdown = """
# Real Heading

```
# Fake heading in code block
```

## Another real heading
"""
        code_blocks = _find_code_blocks(markdown)
        headings = _extract_headings(markdown, code_blocks)
        
        # Should only find the real headings
        assert len(headings) == 2
        assert headings[0][1] == "Real Heading"
        assert headings[1][1] == "Another real heading"


class TestTableOfContents:
    """Tests for table of contents generation."""

    def test_toc_with_duplicate_links(self):
        """Test creating TOC links with duplicates."""
        # Test duplicate link handling
        used_links = {"heading": 1}
        link = _create_toc_link("Heading", used_links)
        assert link == "heading-2"
        assert used_links["heading"] == 2

    def test_empty_headings(self):
        """Test TOC generation with no headings."""
        markdown = "This is text without any headings."
        result = generate_table_of_contents(markdown)
        # Should return the original markdown unchanged
        assert result == markdown


class TestBodyWidth:
    """Tests for body width validation."""

    def test_invalid_body_width_type(self):
        """Test validation for non-integer body width."""
        with pytest.raises(WebdownError) as exc_info:
            _validate_body_width("80")  # String instead of int
        assert "must be an integer" in str(exc_info.value)

    def test_negative_body_width(self):
        """Test validation for negative body width."""
        with pytest.raises(WebdownError) as exc_info:
            _validate_body_width(-10)
        assert "must be a non-negative integer" in str(exc_info.value)