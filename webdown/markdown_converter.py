"""HTML to Markdown conversion functionality.

This module handles conversion of HTML content to Markdown with optional features:
- HTML to Markdown conversion using html2text
- Table of contents generation
- Content selection with CSS selectors
- Compact output mode
- Removal of invisible characters

The main function is html_to_markdown(), but this module also provides
helper functions for each conversion step.
"""

import re
from typing import List, Tuple

import html2text

from webdown.config import WebdownConfig, WebdownError
from webdown.html_parser import extract_content_with_css, validate_css_selector


def _find_code_blocks(markdown: str) -> List[Tuple[int, int]]:
    """Find code blocks in markdown to avoid treating code as headings.

    Args:
        markdown: Markdown content to scan

    Returns:
        List of (start, end) positions of code blocks
    """
    code_blocks = []
    # Find all code blocks (fenced with ```)
    fenced_matches = list(re.finditer(r"```.*?\n.*?```", markdown, re.DOTALL))
    for match in fenced_matches:
        code_blocks.append((match.start(), match.end()))
    return code_blocks


def _is_position_in_code_block(
    position: int, code_blocks: List[Tuple[int, int]]
) -> bool:
    """Check if a given position is inside a code block.

    Args:
        position: The position to check
        code_blocks: List of (start, end) positions of code blocks

    Returns:
        True if position is within a code block, False otherwise
    """
    return any(start <= position <= end for start, end in code_blocks)


def _extract_headings(
    markdown: str, code_blocks: List[Tuple[int, int]]
) -> List[Tuple[str, str]]:
    """Extract headings from markdown, excluding those in code blocks.

    Args:
        markdown: Markdown content to extract headings from
        code_blocks: List of (start, end) positions of code blocks

    Returns:
        List of (heading_markers, heading_title) tuples
    """
    headings = []
    heading_matches = re.finditer(r"^(#{1,6})\s+(.+)$", markdown, re.MULTILINE)

    for match in heading_matches:
        # Skip headings that are inside code blocks
        if _is_position_in_code_block(match.start(), code_blocks):
            continue

        # If not in code block, extract and add heading
        headings.append((match.group(1), match.group(2)))

    return headings


def _create_toc_link(title: str, used_links: dict[str, int]) -> str:
    """Create a URL-friendly link from a heading title.

    Args:
        title: The heading title
        used_links: Dictionary tracking used link names

    Returns:
        URL-friendly link text
    """
    # 1. Convert to lowercase
    # 2. Replace spaces with hyphens
    # 3. Remove special characters
    link = title.lower().replace(" ", "-")
    # Remove non-alphanumeric chars except hyphens
    link = re.sub(r"[^\w\-]", "", link)

    # Handle duplicate links by adding a suffix
    if link in used_links:
        used_links[link] += 1
        link = f"{link}-{used_links[link]}"
    else:
        used_links[link] = 1

    return link


def generate_table_of_contents(markdown: str) -> str:
    """Generate a table of contents based on Markdown headings.

    Args:
        markdown: Markdown content with headings

    Returns:
        Table of contents in Markdown format
    """
    # Find code blocks to exclude from heading search
    code_blocks = _find_code_blocks(markdown)

    # Extract headings, excluding those in code blocks
    headings = _extract_headings(markdown, code_blocks)

    if not headings:
        return markdown

    # Generate table of contents
    toc = ["# Table of Contents\n"]
    used_links: dict[str, int] = {}  # Track used links to avoid duplicates

    for markers, title in headings:
        level = len(markers) - 1  # Adjust for 0-based indentation
        indent = "  " * level
        link = _create_toc_link(title, used_links)
        toc.append(f"{indent}- [{title}](#{link})")

    return "\n".join(toc) + "\n\n" + markdown


def clean_markdown(markdown: str, compact_output: bool = False) -> str:
    """Clean Markdown content by removing invisible characters and extra blank lines.

    Args:
        markdown: Markdown content to clean
        compact_output: Whether to remove excessive blank lines

    Returns:
        Cleaned Markdown content
    """
    # Remove zero-width spaces and other invisible characters
    markdown = re.sub(r"[\u200B\u200C\u200D\uFEFF]", "", markdown)

    # Post-process to remove excessive blank lines if requested
    if compact_output:
        # Replace 3 or more consecutive newlines with just 2
        markdown = re.sub(r"\n{3,}", "\n\n", markdown)

    return markdown


def _validate_body_width(body_width: int) -> None:
    """Validate body_width parameter.

    Args:
        body_width: The body width to validate

    Raises:
        WebdownError: If body_width is invalid
    """
    if not isinstance(body_width, int):
        raise WebdownError(
            f"body_width must be an integer, got {type(body_width).__name__}"
        )
    if body_width < 0:
        raise WebdownError(
            f"body_width must be a non-negative integer, got {body_width}"
        )


def _configure_html2text(config: WebdownConfig) -> html2text.HTML2Text:
    """Configure HTML2Text converter based on config options.

    Args:
        config: Configuration options

    Returns:
        Configured HTML2Text instance
    """
    h = html2text.HTML2Text()

    # Set core options
    h.ignore_links = not config.include_links
    h.ignore_images = not config.include_images
    h.body_width = config.body_width  # User-defined line width

    # Always use Unicode mode for better character representation
    h.unicode_snob = True

    # Use default values for other options
    h.single_line_break = False
    h.bypass_tables = False

    return h


def _validate_config(config: WebdownConfig) -> None:
    """Validate all configuration parameters.

    This centralizes validation logic for WebdownConfig parameters.

    Args:
        config: Configuration to validate

    Raises:
        WebdownError: If any configuration values are invalid
    """
    # Validate body width
    _validate_body_width(config.body_width)

    # Validate CSS selector if provided
    if config.css_selector:
        validate_css_selector(config.css_selector)


def html_to_markdown(
    html: str,
    config: WebdownConfig,
) -> str:
    """Convert HTML to Markdown with formatting options.

    This function takes HTML content and converts it to Markdown format
    based on the provided configuration object.

    Args:
        html: HTML content to convert
        config: Configuration options for the conversion

    Returns:
        Converted Markdown content

    Examples:
        >>> html = "<h1>Title</h1><p>Content with <a href='#'>link</a></p>"
        >>> config = WebdownConfig()
        >>> print(html_to_markdown(html, config))
        # Title

        Content with [link](#)

        >>> config = WebdownConfig(include_links=False)
        >>> print(html_to_markdown(html, config))
        # Title

        Content with link
    """
    # Validate all configuration parameters
    _validate_config(config)

    # Extract specific content by CSS selector if provided
    if config.css_selector:
        html = extract_content_with_css(html, config.css_selector)

    # Configure and run html2text
    converter = _configure_html2text(config)
    markdown = converter.handle(html)

    # Clean up the markdown
    markdown = clean_markdown(markdown, config.compact_output)

    # Add table of contents if requested
    if config.include_toc:
        markdown = generate_table_of_contents(markdown)

    return str(markdown)
