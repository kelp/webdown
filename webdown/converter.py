"""HTML to Markdown and Claude XML conversion functionality.

This module handles fetching web content and converting it to Markdown or Claude XML.
Key features include:
- URL validation and HTML fetching with proper error handling
- HTML to Markdown conversion using html2text
- Support for content filtering with CSS selectors
- Table of contents generation
- Removal of excessive blank lines (compact mode)
- Removal of zero-width spaces and other invisible characters
- Claude XML output format for AI context optimization

The main entry points are `convert_url_to_markdown` and `convert_url_to_claude_xml`,
which handle the entire process from fetching a URL to producing clean output.
"""

import datetime
import io
import re
import xml.sax.saxutils as saxutils
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

import html2text
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


@dataclass
class ClaudeXMLConfig:
    """Configuration options for Claude XML output format.

    This class contains settings specific to the Claude XML output format,
    providing options to customize the structure and metadata of the generated document.

    Attributes:
        include_metadata (bool): Include metadata section with title, source URL, date
        add_date (bool): Include current date in the metadata section
        doc_tag (str): Root document tag name
        beautify (bool): Add indentation and newlines for human readability
    """

    include_metadata: bool = True
    add_date: bool = True
    doc_tag: str = "claude_documentation"
    beautify: bool = True


@dataclass
class WebdownConfig:
    """Configuration options for HTML to Markdown conversion.

    This class centralizes all configuration options for the conversion process,
    focusing on the most useful options for LLM documentation processing.

    Attributes:
        url (Optional[str]): URL of the web page to convert
        include_links (bool): Whether to include hyperlinks (True) or plain text (False)
        include_images (bool): Whether to include images (True) or exclude them
        include_toc (bool): Whether to generate table of contents
        css_selector (Optional[str]): CSS selector to extract specific content
        compact_output (bool): Whether to remove excessive blank lines
        body_width (int): Maximum line length for wrapping (0 for no wrapping)
        show_progress (bool): Whether to display a progress bar during download
    """

    # Core options
    url: Optional[str] = None
    include_links: bool = True
    include_images: bool = True
    include_toc: bool = False
    css_selector: Optional[str] = None
    compact_output: bool = False
    body_width: int = 0
    show_progress: bool = False


class WebdownError(Exception):
    """Exception for webdown errors.

    This exception class is used for all errors raised by the webdown package.
    The error type is indicated by a descriptive message and can be
    distinguished by checking the message content.

    Error types include:
        URL format errors: When the URL doesn't follow standard format
        Network errors: Connection issues, timeouts, HTTP errors
        Parsing errors: Issues with processing the HTML content
    """

    pass


def validate_url(url: str) -> bool:
    """Validate URL format.

    Args:
        url: URL to validate

    Returns:
        True if valid, False otherwise

    >>> validate_url('https://example.com')
    True
    >>> validate_url('http://example.com')
    True
    >>> validate_url('not_a_url')
    False
    """
    if not isinstance(url, str):
        return False

    if not url.strip():
        return False

    parsed = urlparse(url)

    # Check for required components
    has_scheme = bool(parsed.scheme)
    has_netloc = bool(parsed.netloc)

    return has_scheme and has_netloc


def _create_progress_bar(url: str, total_size: int, show_progress: bool) -> tqdm:
    """Create a progress bar for downloading content.

    Args:
        url: URL being downloaded
        total_size: Total size in bytes (0 if unknown)
        show_progress: Whether to display the progress bar

    Returns:
        Configured tqdm progress bar instance
    """
    # Extract page name for the progress description
    page_name = url.split("/")[-1] or "webpage"

    # Create progress bar - if content-length is unknown (0),
    # tqdm will show a progress bar without the total
    return tqdm(
        total=total_size if total_size > 0 else None,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
        desc=f"Downloading {page_name}",
        disable=not show_progress,
    )


def _process_response_chunks(
    response: requests.Response, progress_bar: tqdm, chunk_size: int
) -> str:
    """Process response chunks and update progress bar.

    Args:
        response: The HTTP response object
        progress_bar: Progress bar to update
        chunk_size: Size of chunks to read in bytes

    Returns:
        Complete response content as string
    """
    # Create a buffer to store the content
    content = io.StringIO()

    # Process chunks consistently, handling both str and bytes
    for chunk in response.iter_content(chunk_size=chunk_size):
        if chunk:
            # Calculate chunk size for progress bar
            chunk_len = (
                len(chunk) if isinstance(chunk, bytes) else len(chunk.encode("utf-8"))
            )
            # Decode bytes for StringIO if needed
            text_chunk = (
                chunk.decode("utf-8", errors="replace")
                if isinstance(chunk, bytes)
                else chunk
            )

            # Update progress with correct size
            progress_bar.update(chunk_len)
            # Store in string buffer
            content.write(text_chunk)

    return content.getvalue()


def _handle_small_response(
    response: requests.Response, show_progress: bool
) -> Optional[str]:
    """Handle small responses without streaming for better performance.

    Args:
        response: HTTP response object
        show_progress: Whether progress bar is requested

    Returns:
        Response text for small content, None otherwise
    """
    # Skip streaming for non-progress requests with small content
    if not show_progress and "content-length" in response.headers:
        content_length = int(response.headers.get("content-length", 0))
        if content_length < 1024 * 1024:  # 1MB
            return response.text
    return None


def _handle_request_exception(e: Exception, url: str) -> None:
    """Convert request exceptions to WebdownError with appropriate messages.

    Args:
        e: The exception that was raised
        url: The URL being fetched

    Raises:
        WebdownError: With appropriate error message
    """
    if isinstance(e, requests.exceptions.Timeout):
        raise WebdownError(f"Connection timed out while fetching {url}")
    elif isinstance(e, requests.exceptions.ConnectionError):
        raise WebdownError(f"Connection error while fetching {url}")
    elif isinstance(e, requests.exceptions.HTTPError):
        raise WebdownError(f"HTTP error {e.response.status_code} while fetching {url}")
    else:
        raise WebdownError(f"Error fetching {url}: {str(e)}")


def fetch_url_with_progress(
    url: str, show_progress: bool = False, chunk_size: int = 1024, timeout: int = 10
) -> str:
    """Fetch content from URL with streaming and optional progress bar.

    Args:
        url: URL to fetch
        show_progress: Whether to display a progress bar during download
        chunk_size: Size of chunks to read in bytes
        timeout: Request timeout in seconds

    Returns:
        Content as string

    Raises:
        WebdownError: If content cannot be fetched
    """
    # Note: URL validation is now centralized in _get_normalized_config
    # We assume URL is already validated when this function is called

    try:
        # Make a GET request with stream=True for both cases
        response = requests.get(url, timeout=timeout, stream=True)
        response.raise_for_status()

        # Try to handle small responses without streaming for performance
        small_response = _handle_small_response(response, show_progress)
        if small_response is not None:
            return small_response

        # For larger responses or when progress is requested, use streaming
        total_size = int(response.headers.get("content-length", 0))
        with _create_progress_bar(url, total_size, show_progress) as progress_bar:
            return _process_response_chunks(response, progress_bar, chunk_size)

    except (
        requests.exceptions.Timeout,
        requests.exceptions.ConnectionError,
        requests.exceptions.HTTPError,
        requests.exceptions.RequestException,
    ) as e:
        # This function raises a WebdownError with appropriate message
        _handle_request_exception(e, url)
        # The line below is never reached but needed for type checking
        raise RuntimeError("This should never be reached")


def fetch_url(url: str, show_progress: bool = False) -> str:
    """Fetch HTML content from URL with optional progress bar.

    This is a simplified wrapper around fetch_url_with_progress with default parameters.

    Args:
        url: URL to fetch
        show_progress: Whether to display a progress bar during download

    Returns:
        HTML content as string

    Raises:
        WebdownError: If URL is invalid or content cannot be fetched
    """
    # Validate URL for backward compatibility with tests
    # In normal usage, URL is already validated by _get_normalized_config
    if not validate_url(url):
        raise WebdownError(f"Invalid URL format: {url}")

    return fetch_url_with_progress(url, show_progress, chunk_size=1024, timeout=10)


def validate_css_selector(css_selector: str) -> None:
    """Validate CSS selector format and syntax.

    Args:
        css_selector: CSS selector to validate

    Raises:
        WebdownError: If the selector is invalid
    """
    if not isinstance(css_selector, str) or not css_selector.strip():
        raise WebdownError("CSS selector must be a non-empty string")

    # Basic validation to catch obvious syntax errors
    invalid_chars = ["<", ">", "(", ")", "@"]
    if any(char in css_selector for char in invalid_chars):
        raise WebdownError(
            f"Invalid CSS selector: '{css_selector}'. Contains invalid characters."
        )


def extract_content_with_css(html: str, css_selector: str) -> str:
    """Extract specific content from HTML using a CSS selector.

    CSS selector is assumed to be already validated before this function is called.

    Args:
        html: HTML content
        css_selector: CSS selector to extract content (pre-validated)

    Returns:
        HTML content of selected elements

    Raises:
        WebdownError: If there is an error applying the selector
    """
    import warnings

    # Note: No validation here - validation is now centralized in html_to_markdown

    try:
        soup = BeautifulSoup(html, "html.parser")
        selected = soup.select(css_selector)
        if selected:
            return "".join(str(element) for element in selected)
        else:
            # Warning - no elements matched
            warnings.warn(f"CSS selector '{css_selector}' did not match any elements")
            return html
    except Exception as e:
        raise WebdownError(f"Error applying CSS selector '{css_selector}': {str(e)}")


def _find_code_blocks(markdown: str) -> list[tuple[int, int]]:
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
    position: int, code_blocks: list[tuple[int, int]]
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
    markdown: str, code_blocks: list[tuple[int, int]]
) -> list[tuple[str, str]]:
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
) -> tuple[str, list[tuple[int, Optional[str], str]]]:
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
) -> list[str]:
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
    code_blocks: list[tuple[int, Optional[str], str]],
    indent_level: int,
    beautify: bool,
) -> list[str]:
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
    placeholder: str, code_blocks: list, indent_level: int, beautify: bool
) -> list[str]:
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


def _process_text_paragraph(para: str, indent_level: int, beautify: bool) -> list[str]:
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
    paragraphs: list[str], code_blocks: list, indent_level: int, beautify: bool
) -> list[str]:
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
    heading: str, content: str, code_blocks: list, beautify: bool
) -> list[str]:
    """Process a markdown section with heading and content.

    Args:
        heading: The section heading string
        content: The section content string
        code_blocks: List of extracted code blocks
        beautify: Whether to apply indentation

    Returns:
        List of XML strings for the section
    """
    xml_parts: list[str] = []

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
    markdown: str, code_blocks: list, beautify: bool
) -> list[str]:
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


def _process_pre_heading_content(content: str, beautify: bool) -> list[str]:
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


def _get_section_pairs(sections: list[str]) -> list[tuple[str, str]]:
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
    sections: list[str], code_blocks: list, beautify: bool
) -> list[str]:
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
) -> list[str]:
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
    placeholder_md: str, code_blocks: list, beautify: bool
) -> list[str]:
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
) -> list[str]:
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


def convert_url_to_claude_xml(
    url_or_config: str | WebdownConfig,
    claude_xml_config: Optional[ClaudeXMLConfig] = None,
) -> str:
    """Convert a web page directly to Claude XML format.

    This function fetches a web page and converts it to Claude XML format,
    optimized for use with Claude AI models.

    Args:
        url_or_config: URL to fetch or WebdownConfig object
        claude_xml_config: XML output configuration

    Returns:
        Claude XML formatted content

    Raises:
        WebdownError: If URL is invalid or cannot be fetched
    """
    # Determine source URL for metadata
    source_url = url_or_config if isinstance(url_or_config, str) else url_or_config.url

    # Use the existing markdown conversion pipeline - keep the original parameter type
    # for backward compatibility with tests
    markdown = convert_url_to_markdown(url_or_config)

    # Convert the markdown to Claude XML
    return markdown_to_claude_xml(markdown, source_url, claude_xml_config)


def _get_normalized_config(url_or_config: str | WebdownConfig) -> WebdownConfig:
    """Get a normalized WebdownConfig object with validated URL.

    This function centralizes URL validation logic for the entire converter module.
    All code paths that need a validated URL should go through this function.

    Args:
        url_or_config: URL string or WebdownConfig object

    Returns:
        Normalized WebdownConfig with validated URL

    Raises:
        WebdownError: If URL is invalid or missing
    """
    # Create config object if a URL string was provided
    if isinstance(url_or_config, str):
        config = WebdownConfig(url=url_or_config)
    else:
        config = url_or_config
        if config.url is None:
            raise WebdownError("URL must be provided in the config object")

    # At this point config.url cannot be None due to the check above
    url = config.url
    assert url is not None

    # Validate URL format - centralized validation for the entire module
    if not validate_url(url):
        raise WebdownError(f"Invalid URL format: {url}")

    return config


def _check_streaming_needed(url: str) -> bool:
    """Check if streaming is needed based on content size.

    Args:
        url: URL to check (assumed to be already validated)

    Returns:
        True if streaming should be used, False otherwise
    """
    # Fixed streaming threshold at 10MB
    STREAM_THRESHOLD = 10 * 1024 * 1024

    try:
        # Use HEAD request to check content length without full download
        head_response = requests.head(url, timeout=5)
        content_length = int(head_response.headers.get("content-length", "0"))
        return content_length > STREAM_THRESHOLD
    except (requests.RequestException, ValueError):
        # If HEAD request fails or content-length is invalid,
        # default to False (non-streaming) as a safe fallback
        return False


def convert_url_to_markdown(url_or_config: str | WebdownConfig) -> str:
    """Convert a web page to markdown.

    This function accepts either a URL string or a WebdownConfig object.
    If a URL string is provided, it will be used to create a WebdownConfig object.

    For large web pages (over 10MB), streaming mode is automatically used.

    Args:
        url_or_config: URL of the web page or a WebdownConfig object

    Returns:
        Markdown content

    Raises:
        WebdownError: If URL is invalid or cannot be fetched

    Examples:
        # Using URL string
        markdown = convert_url_to_markdown("https://example.com")

        # Using config object
        config = WebdownConfig(
            url="https://example.com",
            include_toc=True,
            show_progress=True
        )
        markdown = convert_url_to_markdown(config)
    """
    # Get normalized config with validated URL
    config = _get_normalized_config(url_or_config)
    # At this point, the URL has been validated and cannot be None
    url = config.url
    assert url is not None

    try:
        # Check if streaming is needed based on content size
        # This is mainly for compatibility with tests that expect this behavior
        _check_streaming_needed(url)

        # Fetch the HTML content (URL already validated by _get_normalized_config)
        html = fetch_url(url, show_progress=config.show_progress)

        # Convert HTML to Markdown
        return html_to_markdown(html, config)

    except requests.exceptions.RequestException as e:
        # This is a fallback for any other request exceptions
        raise WebdownError(f"Error fetching {url}: {str(e)}")
