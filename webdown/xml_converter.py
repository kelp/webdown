"""Markdown to Claude XML conversion functionality.

This module handles conversion of Markdown content to Claude XML format:
- Processes code blocks directly (no placeholders)
- Handles headings, sections, and paragraphs
- Generates metadata when requested
- Creates a structured XML document for use with Claude

The main function is markdown_to_claude_xml(), which converts Markdown
content to a format suitable for Claude AI models.
"""

import datetime
import re
import xml.sax.saxutils as saxutils
from typing import List, Match, Optional


def escape_xml(text: str) -> str:
    """Escape XML special characters.

    Args:
        text: Text to escape

    Returns:
        Escaped text
    """
    return saxutils.escape(text)


def indent_xml(text: str, level: int = 0) -> str:
    """Add indentation to text.

    Args:
        text: Text to indent
        level: Indentation level (2 spaces per level)

    Returns:
        Indented text
    """
    indent_str = "  " * level
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


def generate_metadata_xml(title: Optional[str], source_url: Optional[str]) -> List[str]:
    """Generate XML metadata section.

    Args:
        title: Document title
        source_url: Source URL

    Returns:
        List of XML strings for metadata section
    """
    metadata_items = []

    if title:
        metadata_items.append(indent_xml(f"<title>{escape_xml(title)}</title>", 1))
    if source_url:
        metadata_items.append(
            indent_xml(f"<source>{escape_xml(source_url)}</source>", 1)
        )

    # Always include date
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    metadata_items.append(indent_xml(f"<date>{today}</date>", 1))

    result = [indent_xml("<metadata>", 1)]
    result.extend(metadata_items)
    result.append(indent_xml("</metadata>", 1))

    return result


def process_code_block(match: Match[str], level: int) -> List[str]:
    """Process a code block and convert to XML format.

    Args:
        match: Regex match object for the code block
        level: Indentation level

    Returns:
        List of XML strings for the code block
    """
    lang = match.group(1).strip()
    code = match.group(2)

    result = []

    # Opening tag
    if lang:
        result.append(indent_xml(f'<code language="{lang}">', level))
    else:
        result.append(indent_xml("<code>", level))

    # Code content - indent each line
    for line in code.split("\n"):
        result.append(indent_xml(escape_xml(line), level + 1))

    # Closing tag
    result.append(indent_xml("</code>", level))

    return result


def process_paragraph(text: str, level: int) -> str:
    """Process a regular text paragraph into XML.

    Args:
        text: Paragraph text
        level: Indentation level

    Returns:
        XML string for the paragraph
    """
    return indent_xml(f"<text>{escape_xml(text)}</text>", level)


def _process_paragraphs(content: str, level: int) -> List[str]:
    """Process content into paragraphs, handling empty paragraphs and code blocks.
    
    Args:
        content: The text content to process
        level: The indentation level for XML elements
        
    Returns:
        List of XML strings representing the processed paragraphs
    """
    result = []
    paragraphs = re.split(r"\n\n+", content)
    for para in paragraphs:
        if not para.strip():
            continue
        
        # Check if it's a code block
        code_match = re.match(r"```(\w*)\n(.*?)```", para, re.DOTALL)
        if code_match:
            result.extend(process_code_block(code_match, level))
        else:
            result.append(process_paragraph(para, level))
    
    return result


def process_section(match: Match[str], level: int) -> List[str]:
    """Process a section (heading + content) into XML.

    Args:
        match: Regex match containing heading and content
        level: Indentation level

    Returns:
        List of XML strings for the section
    """
    heading_text = match.group(2).strip()
    content = match.group(3).strip() if match.group(3) else ""

    result = []

    # Open section
    result.append(indent_xml("<section>", level))

    # Add heading
    result.append(
        indent_xml(f"<heading>{escape_xml(heading_text)}</heading>", level + 1)
    )

    # Process content
    if content:
        result.extend(_process_paragraphs(content, level + 1))

    # Close section
    result.append(indent_xml("</section>", level))

    return result


def markdown_to_claude_xml(
    markdown: str,
    source_url: Optional[str] = None,
    include_metadata: bool = True,
) -> str:
    """Convert Markdown content to Claude XML format.

    This function converts Markdown content to a structured XML format
    suitable for use with Claude AI models. It handles elements like
    headings, paragraphs, and code blocks, organizing them into a
    hierarchical XML document.

    Args:
        markdown: Markdown content to convert
        source_url: Source URL for the content (for metadata)
        include_metadata: Whether to include metadata section (title, source, date)

    Returns:
        Claude XML formatted content
    """
    xml_parts = []

    # Use a fixed document tag - simplifying configuration
    doc_tag = "claude_documentation"

    # Root element
    xml_parts.append(f"<{doc_tag}>")

    # Extract title
    title = extract_markdown_title(markdown)

    # Add metadata if requested
    if include_metadata:
        xml_parts.extend(generate_metadata_xml(title, source_url))

    # Begin content section
    xml_parts.append(indent_xml("<content>", 1))

    # Process all content by section

    # Extract all section headings
    section_matches = list(re.finditer(r"^(#+\s+)(.+?)$", markdown, re.MULTILINE))

    if section_matches:
        # Process each section including content following the heading
        for i, match in enumerate(section_matches):
            heading_start = match.start()
            heading = match.group(0)
            # If this is the last heading, content goes to the end
            if i == len(section_matches) - 1:
                content = markdown[heading_start + len(heading) :].strip()
            else:
                # Otherwise content goes until the next heading
                next_heading_start = section_matches[i + 1].start()
                content = markdown[
                    heading_start + len(heading) : next_heading_start
                ].strip()

            # Create section with heading and content
            section_xml = []
            section_xml.append(indent_xml("<section>", 2))
            section_xml.append(
                indent_xml(
                    f"<heading>{escape_xml(match.group(2).strip())}</heading>", 3
                )
            )

            # Process content inside this section
            if content:
                section_xml.extend(_process_paragraphs(content, 3))

            section_xml.append(indent_xml("</section>", 2))
            xml_parts.extend(section_xml)

        # Process content before the first heading (if any)
        if section_matches[0].start() > 0:
            pre_content = markdown[: section_matches[0].start()].strip()
            if pre_content:
                # Add pre-heading content at the beginning
                pre_parts = _process_paragraphs(pre_content, 2)

                xml_parts = xml_parts[:2] + pre_parts + xml_parts[2:]
    else:
        # No headings - just process all content
        xml_parts.extend(_process_paragraphs(markdown, 2))

    # Close content and root
    xml_parts.append(indent_xml("</content>", 1))
    xml_parts.append(f"</{doc_tag}>")

    return "\n".join(xml_parts)
