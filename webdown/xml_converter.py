"""Markdown to Claude XML conversion functionality.

This module handles conversion of Markdown content to Claude XML format:
- Extracts and processes code blocks
- Parses headings and sections
- Handles metadata generation
- Organizes content into a structured XML document

The main function is markdown_to_claude_xml(), but this module also provides
helper functions for each conversion step.
"""

import datetime
import re
import xml.sax.saxutils as saxutils
from typing import List, Optional, Tuple

from webdown.config import ClaudeXMLConfig


def escape_xml(text: str) -> str:
    """Escape XML special characters.

    Args:
        text: Text to escape

    Returns:
        Escaped text
    """
    return saxutils.escape(text)


def indent_xml(
    text: str, level: int = 0, spaces: int = 2, beautify: bool = True
) -> str:
    """Add indentation to text if beautify is enabled.

    Args:
        text: Text to indent
        level: Indentation level
        spaces: Number of spaces per indentation level
        beautify: Whether to apply indentation

    Returns:
        Indented text if beautify is True, otherwise original text
    """
    if not beautify:
        return text
    indent_str = " " * spaces * level
    return f"{indent_str}{text}"


def extract_markdown_title(markdown: str) -> Optional[str]:
    """Extract title from first heading in Markdown content.

    Args:
        markdown: Markdown content

    Returns:
        Title text or None if no title found
    """
    title_match = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
    if title_match:
        return title_match.group(1).strip()
    return None


def extract_code_blocks(
    markdown: str,
) -> Tuple[str, List[Tuple[int, Optional[str], str]]]:
    """Extract code blocks from Markdown and replace with placeholders.

    Args:
        markdown: Markdown content

    Returns:
        Tuple containing:
        - Modified markdown with placeholders
        - List of tuples with (id, language, code) for each block
    """
    code_blocks = []
    code_pattern = re.compile(r"```(\w*)\n(.*?)```", re.DOTALL)
    code_matches = list(code_pattern.finditer(markdown))

    # Replace code blocks with placeholders to protect them during processing
    placeholder_md = markdown
    for i, match in enumerate(code_matches):
        lang = match.group(1).strip() or None
        code = match.group(2)
        code_blocks.append((i, lang, code))
        placeholder = f"CODE_BLOCK_PLACEHOLDER_{i}"
        placeholder_md = placeholder_md.replace(match.group(0), placeholder)

    return placeholder_md, code_blocks


def generate_metadata_xml(
    title: Optional[str], source_url: Optional[str], add_date: bool, beautify: bool
) -> List[str]:
    """Generate XML metadata section.

    Args:
        title: Document title
        source_url: Source URL
        add_date: Whether to include current date
        beautify: Whether to format with indentation

    Returns:
        List of XML strings for metadata section
    """
    metadata_items = []

    if title:
        metadata_items.append(
            indent_xml(f"<title>{escape_xml(title)}</title>", 1, beautify=beautify)
        )
    if source_url:
        metadata_items.append(
            indent_xml(
                f"<source>{escape_xml(source_url)}</source>", 1, beautify=beautify
            )
        )
    if add_date:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        metadata_items.append(indent_xml(f"<date>{today}</date>", 1, beautify=beautify))

    if not metadata_items:
        return []

    result = [indent_xml("<metadata>", 1, beautify=beautify)]
    result.extend(metadata_items)
    result.append(indent_xml("</metadata>", 1, beautify=beautify))

    return result


def process_code_block(
    block_id: int,
    code_blocks: List[Tuple[int, Optional[str], str]],
    indent_level: int,
    beautify: bool,
) -> List[str]:
    """Process a code block and convert to XML format.

    Args:
        block_id: ID of the code block
        code_blocks: List of code blocks
        indent_level: Indentation level
        beautify: Whether to apply indentation

    Returns:
        List of XML strings for the code block
    """
    _, lang, code = code_blocks[block_id]
    xml_parts = []

    if lang:
        xml_parts.append(
            indent_xml(f'<code language="{lang}">', indent_level, beautify=beautify)
        )
    else:
        xml_parts.append(indent_xml("<code>", indent_level, beautify=beautify))

    # Add code with proper indentation
    for line in code.split("\n"):
        xml_parts.append(
            indent_xml(escape_xml(line), indent_level + 1, beautify=beautify)
        )

    xml_parts.append(indent_xml("</code>", indent_level, beautify=beautify))

    return xml_parts


def _process_code_placeholder(
    placeholder: str, code_blocks: List, indent_level: int, beautify: bool
) -> List[str]:
    """Process a code block placeholder.

    Args:
        placeholder: The placeholder string
        code_blocks: List of extracted code blocks
        indent_level: Current indentation level
        beautify: Whether to apply indentation

    Returns:
        List of XML strings for the code block or empty list if not a placeholder
    """
    code_match = re.match(r"CODE_BLOCK_PLACEHOLDER_(\d+)", placeholder)
    if not code_match:
        return []

    block_id = int(code_match.group(1))
    return process_code_block(block_id, code_blocks, indent_level, beautify)


def _process_text_paragraph(para: str, indent_level: int, beautify: bool) -> List[str]:
    """Process a normal text paragraph into XML.

    Args:
        para: The paragraph text
        indent_level: Current indentation level
        beautify: Whether to apply indentation

    Returns:
        List containing the XML element for the paragraph
    """
    return [
        indent_xml(f"<text>{escape_xml(para)}</text>", indent_level, beautify=beautify)
    ]


def _process_markdown_paragraphs(
    paragraphs: List[str], code_blocks: List, indent_level: int, beautify: bool
) -> List[str]:
    """Process markdown paragraphs and convert them to XML elements.

    Args:
        paragraphs: List of paragraph strings to process
        code_blocks: List of extracted code blocks
        indent_level: Current indentation level
        beautify: Whether to apply indentation

    Returns:
        List of XML strings for the paragraphs
    """
    xml_parts = []

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # Process code block placeholders
        code_xml = _process_code_placeholder(para, code_blocks, indent_level, beautify)
        if code_xml:
            xml_parts.extend(code_xml)
            continue

        # Process regular text paragraphs
        xml_parts.extend(_process_text_paragraph(para, indent_level, beautify))

    return xml_parts


def _extract_heading_text(heading: str) -> Optional[str]:
    """Extract the text from a markdown heading.

    Args:
        heading: The heading string (e.g., "## Heading Text")

    Returns:
        The extracted heading text or None if invalid
    """
    heading_match = re.match(r"(#{1,6})\s+(.+)$", heading)
    if not heading_match:
        return None

    return heading_match.group(2).strip()


def _process_markdown_section(
    heading: str, content: str, code_blocks: List, beautify: bool
) -> List[str]:
    """Process a markdown section with heading and content.

    Args:
        heading: The section heading string
        content: The section content string
        code_blocks: List of extracted code blocks
        beautify: Whether to apply indentation

    Returns:
        List of XML strings for the section
    """
    xml_parts: List[str] = []

    # Extract heading text
    heading_text = _extract_heading_text(heading)
    if heading_text is None:
        return xml_parts

    # Add section and heading
    xml_parts.append(indent_xml("<section>", 2, beautify=beautify))
    xml_parts.append(
        indent_xml(
            f"<heading>{escape_xml(heading_text)}</heading>", 3, beautify=beautify
        )
    )

    # Process content paragraphs if any
    if content:
        paragraphs = re.split(r"\n\n+", content)
        xml_parts.extend(
            _process_markdown_paragraphs(paragraphs, code_blocks, 3, beautify)
        )

    xml_parts.append(indent_xml("</section>", 2, beautify=beautify))

    return xml_parts


def _is_standalone_code_placeholder(line: str) -> Optional[int]:
    """Check if a line is a standalone code block placeholder.

    Args:
        line: The line to check

    Returns:
        The code block ID if it's a standalone placeholder, or None
    """
    # Skip non-matching lines
    if not line or line.strip() != line:
        return None

    # Check for code placeholder pattern
    code_match = re.match(r"CODE_BLOCK_PLACEHOLDER_(\d+)", line)
    if not code_match:
        return None

    # Return the block ID
    return int(code_match.group(1))


def _process_standalone_code_blocks(
    markdown: str, code_blocks: List, beautify: bool
) -> List[str]:
    """Process code blocks that aren't inside sections.

    Args:
        markdown: The markdown content with placeholders
        code_blocks: List of extracted code blocks
        beautify: Whether to apply indentation

    Returns:
        List of XML strings for the standalone code blocks
    """
    xml_parts = []

    for line in markdown.split("\n"):
        block_id = _is_standalone_code_placeholder(line)
        if block_id is not None:
            xml_parts.extend(process_code_block(block_id, code_blocks, 2, beautify))

    return xml_parts


def _process_pre_heading_content(content: str, beautify: bool) -> List[str]:
    """Process content that appears before the first heading.

    Args:
        content: The content text
        beautify: Whether to apply indentation

    Returns:
        List of XML elements for the content
    """
    if not content.strip():
        return []

    text = content.strip()
    return [indent_xml(f"<text>{escape_xml(text)}</text>", 2, beautify=beautify)]


def _get_section_pairs(sections: List[str]) -> List[Tuple[str, str]]:
    """Extract heading-content pairs from sections list.

    Args:
        sections: List of section strings from the regex split

    Returns:
        List of (heading, content) tuples
    """
    pairs = []

    # Iterate through heading and content pairs
    for i in range(1, len(sections), 2):
        if i + 1 < len(sections):
            heading = sections[i].strip()
            content = sections[i + 1].strip()
            pairs.append((heading, content))

    return pairs


def _process_all_sections(
    sections: List[str], code_blocks: List, beautify: bool
) -> List[str]:
    """Process all markdown sections (headings and their content).

    Args:
        sections: List of section strings from the regex split
        code_blocks: List of extracted code blocks
        beautify: Whether to apply indentation

    Returns:
        List of XML elements for all sections
    """
    xml_parts = []

    # Get all heading-content pairs
    section_pairs = _get_section_pairs(sections)

    # Process each section
    for heading, content in section_pairs:
        xml_parts.extend(
            _process_markdown_section(heading, content, code_blocks, beautify)
        )

    return xml_parts


def _create_xml_root_and_metadata(
    title: Optional[str], source_url: Optional[str], config: ClaudeXMLConfig
) -> List[str]:
    """Create XML root element and metadata section.

    Args:
        title: Document title
        source_url: Source URL
        config: Configuration options

    Returns:
        List of XML strings for root and metadata
    """
    xml_parts = [f"<{config.doc_tag}>"]

    # Add metadata section if requested
    if config.include_metadata:
        metadata_xml = generate_metadata_xml(
            title, source_url, config.add_date, config.beautify
        )
        xml_parts.extend(metadata_xml)

    return xml_parts


def _process_markdown_content(
    placeholder_md: str, code_blocks: List, beautify: bool
) -> List[str]:
    """Process markdown content into XML elements.

    Args:
        placeholder_md: Markdown with code block placeholders
        code_blocks: List of extracted code blocks
        beautify: Whether to apply indentation

    Returns:
        List of XML strings for content section
    """
    xml_parts = []

    # Split into sections based on headings
    sections = re.split(r"(?m)^(#{1,6}\s+.+)$", placeholder_md)

    # Process content before the first heading
    xml_parts.extend(_process_pre_heading_content(sections[0], beautify))

    # Process all heading sections
    xml_parts.extend(_process_all_sections(sections, code_blocks, beautify))

    # Process any code blocks that weren't inside sections
    xml_parts.extend(
        _process_standalone_code_blocks(placeholder_md, code_blocks, beautify)
    )

    return xml_parts


def _build_xml_structure(
    markdown: str, source_url: Optional[str], config: ClaudeXMLConfig
) -> List[str]:
    """Build the full XML structure from markdown content.

    Args:
        markdown: Markdown content to convert
        source_url: Source URL for metadata
        config: Configuration options

    Returns:
        List of XML strings for the complete document
    """
    # Extract document title and code blocks
    title = extract_markdown_title(markdown)
    placeholder_md, code_blocks = extract_code_blocks(markdown)

    # Create root element and metadata
    xml_parts = _create_xml_root_and_metadata(title, source_url, config)

    # Add content section
    xml_parts.append(indent_xml("<content>", 1, beautify=config.beautify))
    xml_parts.extend(
        _process_markdown_content(placeholder_md, code_blocks, config.beautify)
    )
    xml_parts.append(indent_xml("</content>", 1, beautify=config.beautify))

    # Close root element
    xml_parts.append(f"</{config.doc_tag}>")

    return xml_parts


def markdown_to_claude_xml(
    markdown: str,
    source_url: Optional[str] = None,
    config: Optional[ClaudeXMLConfig] = None,
) -> str:
    """Convert Markdown content to Claude XML format.

    This function converts Markdown content to a structured XML format
    suitable for use with Claude AI models. It handles basic elements like
    headings, paragraphs, and code blocks.

    Args:
        markdown: Markdown content to convert
        source_url: Source URL for the content (for metadata)
        config: Configuration options for XML output

    Returns:
        Claude XML formatted content
    """
    if config is None:
        config = ClaudeXMLConfig()

    xml_parts = _build_xml_structure(markdown, source_url, config)
    return "\n".join(xml_parts)
