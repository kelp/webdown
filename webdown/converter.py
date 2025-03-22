"""HTML to Markdown and Claude XML conversion functionality.

This module provides functions for fetching web content and converting it to Markdown or Claude XML.
Key features include:
- URL validation and HTML fetching with proper error handling
- HTML to Markdown conversion using html2text
- Support for content filtering with CSS selectors
- Table of contents generation
- Removal of excessive blank lines (compact mode)
- Removal of zero-width spaces and other invisible characters
- Claude XML output format generation for AI context optimization

The main entry points are the `convert_url_to_markdown` and `convert_url_to_claude_xml` functions,
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
        include_metadata (bool): Include metadata section with title, source URL, and date
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


def fetch_url(url: str, show_progress: bool = False) -> str:
    """Fetch HTML content from URL with optional progress bar.

    Args:
        url: URL to fetch
        show_progress: Whether to display a progress bar during download

    Returns:
        HTML content as string

    Raises:
        WebdownError: If URL is invalid or cannot be fetched
    """
    if not validate_url(url):
        raise WebdownError(f"Invalid URL format: {url}")

    try:
        # Stream the response to show download progress
        if show_progress:
            # Make a GET request with stream=True
            response = requests.get(url, timeout=10, stream=True)
            response.raise_for_status()

            # Get content length from headers if available
            total_size = int(response.headers.get("content-length", 0))

            # Page name for the progress bar
            page_name = url.split("/")[-1] or "webpage"

            # Create a buffer to store the content
            content = io.StringIO()

            # Create progress bar - note that if content-length is unknown (0),
            # tqdm will show a progress bar without the total
            with tqdm(
                total=total_size if total_size > 0 else None,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                desc=f"Downloading {page_name}",
                disable=not show_progress,
            ) as progress_bar:
                # Process chunks consistently, handling both str and bytes
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        # Calculate chunk size for progress bar
                        if isinstance(chunk, bytes):
                            chunk_size = len(chunk)
                            # Decode bytes for StringIO
                            text_chunk = chunk.decode("utf-8", errors="replace")
                        else:
                            # Handle str chunks (mostly for tests)
                            chunk_size = len(chunk.encode("utf-8"))
                            text_chunk = chunk

                        # Update progress with correct size
                        progress_bar.update(chunk_size)
                        # Store in string buffer
                        content.write(text_chunk)

            return content.getvalue()
        else:
            # Regular request without progress bar
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return str(response.text)
    except requests.exceptions.Timeout:
        raise WebdownError(f"Connection timed out while fetching {url}")
    except requests.exceptions.ConnectionError:
        raise WebdownError(f"Connection error while fetching {url}")
    except requests.exceptions.HTTPError as e:
        raise WebdownError(f"HTTP error {e.response.status_code} while fetching {url}")
    except requests.exceptions.RequestException as e:
        raise WebdownError(f"Error fetching {url}: {str(e)}")


def html_to_markdown(
    html: str,
    include_links: bool = True,
    include_images: bool = True,
    include_toc: bool = False,
    css_selector: Optional[str] = None,
    compact_output: bool = False,
    body_width: int = 0,
    # Config object support
    config: Optional[WebdownConfig] = None,
) -> str:
    """Convert HTML to Markdown with various formatting options.

    This function takes HTML content and converts it to Markdown format.
    It provides many options to customize the output, from basic features like
    link/image handling to advanced formatting options.

    You can provide individual parameters or use a WebdownConfig object.
    If a config object is provided, it takes precedence over individual parameters.

    Args:
        html (str): HTML content to convert as a string
        include_links (bool): Whether to include hyperlinks or convert to plain text
        include_images (bool): Whether to include images (True) or exclude them
        include_toc (bool): Whether to generate table of contents based on headings
        css_selector (Optional[str]): CSS selector to extract specific content
        compact_output (bool): Whether to remove excessive blank lines in the output
        body_width (int): Maximum line length for text wrapping (0 for no wrapping)
        single_line_break (bool): Whether to use single line breaks instead of double
        protect_links (bool): Whether to protect links from line wrapping
        images_as_html (bool): Whether to keep images as HTML rather than Markdown
        unicode_snob (bool): Whether to use Unicode characters instead of ASCII
        tables_as_html (bool): Whether to keep tables as HTML rather than Markdown
        emphasis_mark (str): Character to use for emphasis (default: "_")
        strong_mark (str): Character to use for strong emphasis (default: "**")
        default_image_alt (str): Default alt text for images without alt attributes
        pad_tables (bool): Whether to add padding spaces for table alignment
        wrap_list_items (bool): Whether to wrap list items to the body_width
        config (Optional[WebdownConfig]): A WebdownConfig object with all options.
            If provided, all other parameters are ignored.

    Returns:
        A string containing the converted Markdown content

    Examples:
        >>> html = "<h1>Title</h1><p>Content with <a href='#'>link</a></p>"
        >>> print(html_to_markdown(html))
        # Title

        Content with [link](#)

        >>> print(html_to_markdown(html, include_links=False))
        # Title

        Content with link

        >>> print(html_to_markdown(html, body_width=40))
        # Title

        Content with [link](#)
    """
    # Extract specific content by CSS selector if provided
    if css_selector:
        # Validate CSS selector format
        if not isinstance(css_selector, str) or not css_selector.strip():
            raise WebdownError("CSS selector must be a non-empty string")

        # Some basic validation to catch obvious syntax errors
        invalid_chars = ["<", ">", "(", ")", "@"]
        if any(char in css_selector for char in invalid_chars):
            raise WebdownError(
                f"Invalid CSS selector: '{css_selector}'. Contains invalid characters."
            )

        try:
            soup = BeautifulSoup(html, "html.parser")
            selected = soup.select(css_selector)
            if selected:
                html = "".join(str(element) for element in selected)
            else:
                # Warning - no elements matched
                import warnings

                warnings.warn(
                    f"CSS selector '{css_selector}' did not match any elements"
                )
        except Exception as e:
            raise WebdownError(
                f"Error applying CSS selector '{css_selector}': {str(e)}"
            )

    # Use config object if provided, otherwise use individual parameters
    if config is not None:
        # Override parameters with config values
        include_links = config.include_links
        include_images = config.include_images
        include_toc = config.include_toc
        css_selector = config.css_selector
        compact_output = config.compact_output
        body_width = config.body_width

    # Validate numeric parameters
    if not isinstance(body_width, int):
        raise WebdownError(
            f"body_width must be an integer, got {type(body_width).__name__}"
        )
    if body_width < 0:
        raise WebdownError(
            f"body_width must be a non-negative integer, got {body_width}"
        )

    # Configure html2text
    h = html2text.HTML2Text()

    # Set core options
    h.ignore_links = not include_links
    h.ignore_images = not include_images
    h.body_width = body_width  # User-defined line width

    # Always use Unicode mode for better character representation
    h.unicode_snob = True

    # Use default values for other options
    h.single_line_break = False
    h.bypass_tables = False

    markdown = h.handle(html)

    # Post-process the markdown
    import re

    # Remove zero-width spaces and other invisible characters
    markdown = re.sub(r"[\u200B\u200C\u200D\uFEFF]", "", markdown)

    # Post-process to remove excessive blank lines if requested
    if compact_output:
        # Replace 3 or more consecutive newlines with just 2
        markdown = re.sub(r"\n{3,}", "\n\n", markdown)

    # Add table of contents if requested
    if include_toc:
        # First identify code blocks to avoid picking up # in code
        code_blocks = []
        # Find all code blocks (both indented and fenced)
        fenced_matches = list(re.finditer(r"```.*?\n.*?```", markdown, re.DOTALL))
        for match in fenced_matches:
            code_blocks.append((match.start(), match.end()))

        # Now find headings outside of code blocks
        headings = []
        heading_matches = re.finditer(r"^(#{1,6})\s+(.+)$", markdown, re.MULTILINE)

        for match in heading_matches:
            # Check if this heading is within a code block
            is_in_code_block = False
            for start, end in code_blocks:
                if start <= match.start() <= end:
                    is_in_code_block = True
                    break

            if not is_in_code_block:
                headings.append((match.group(1), match.group(2)))

        if headings:
            toc = ["# Table of Contents\n"]
            used_links: dict[str, int] = {}  # Track used links to avoid duplicates

            for markers, title in headings:
                level = len(markers) - 1  # Adjust for 0-based indentation
                indent = "  " * level

                # Create a URL-friendly link
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

                toc.append(f"{indent}- [{title}](#{link})")

            markdown = "\n".join(toc) + "\n\n" + markdown

    # The return type is explicitly str, so we ensure it's returned as a string
    return str(markdown)


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
        markdown (str): Markdown content to convert
        source_url (Optional[str]): Source URL for the content (for metadata)
        config (Optional[ClaudeXMLConfig]): Configuration options for XML output

    Returns:
        str: Claude XML formatted content
    """
    if config is None:
        config = ClaudeXMLConfig()

    # Helper functions
    def escape_xml(text: str) -> str:
        """Escape XML special characters."""
        return saxutils.escape(text)

    def indent(text: str, level: int = 0, spaces: int = 2) -> str:
        """Add indentation to text if beautify is enabled."""
        if not config.beautify:
            return text
        indent_str = " " * spaces * level
        return f"{indent_str}{text}"

    # Extract title from first heading
    title = None
    title_match = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()

    # Extract code blocks to prevent processing their content as markdown
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

    # Build the XML document
    xml_parts = []
    xml_parts.append(f"<{config.doc_tag}>")

    # Add metadata section if requested
    if config.include_metadata:
        metadata_items = []
        if title:
            metadata_items.append(indent(f"<title>{escape_xml(title)}</title>", 1))
        if source_url:
            metadata_items.append(
                indent(f"<source>{escape_xml(source_url)}</source>", 1)
            )
        if config.add_date:
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            metadata_items.append(indent(f"<date>{today}</date>", 1))

        if metadata_items:
            xml_parts.append(indent("<metadata>", 1))
            xml_parts.extend(metadata_items)
            xml_parts.append(indent("</metadata>", 1))

    # Add content section
    xml_parts.append(indent("<content>", 1))

    # Process the markdown content with code blocks removed
    # Here we do some basic content processing

    # Split into sections based on headings
    sections = re.split(r"(?m)^(#{1,6}\s+.+)$", placeholder_md)

    # First item will be any content before the first heading
    if sections[0].strip():
        text = sections[0].strip()
        xml_parts.append(indent(f"<text>{escape_xml(text)}</text>", 2))

    # Process sections (each heading and its content)
    for i in range(1, len(sections), 2):
        if i + 1 < len(sections):
            heading = sections[i].strip()
            content = sections[i + 1].strip()

            # Extract heading level and text
            heading_match = re.match(r"(#{1,6})\s+(.+)$", heading)
            if heading_match:
                level = len(heading_match.group(1))
                heading_text = heading_match.group(2).strip()

                # Add section
                xml_parts.append(indent(f"<section>", 2))
                xml_parts.append(
                    indent(f"<heading>{escape_xml(heading_text)}</heading>", 3)
                )

                # Process content paragraphs
                if content:
                    paragraphs = re.split(r"\n\n+", content)
                    for para in paragraphs:
                        para = para.strip()
                        if not para:
                            continue

                        # Check if this paragraph is a code block placeholder
                        code_match = re.match(r"CODE_BLOCK_PLACEHOLDER_(\d+)", para)
                        if code_match:
                            block_id = int(code_match.group(1))
                            _, lang, code = code_blocks[block_id]

                            if lang:
                                xml_parts.append(indent(f'<code language="{lang}">', 3))
                            else:
                                xml_parts.append(indent("<code>", 3))

                            # Add code with proper indentation
                            for line in code.split("\n"):
                                xml_parts.append(indent(escape_xml(line), 4))

                            xml_parts.append(indent("</code>", 3))
                        else:
                            xml_parts.append(
                                indent(f"<text>{escape_xml(para)}</text>", 3)
                            )

                xml_parts.append(indent("</section>", 2))

    # Process any code blocks that weren't inside sections
    # Restore any code blocks that were outside of sections
    for i, placeholder in enumerate(placeholder_md.split("\n")):
        code_match = re.match(r"CODE_BLOCK_PLACEHOLDER_(\d+)", placeholder.strip())
        if code_match and placeholder.strip() == placeholder:
            block_id = int(code_match.group(1))
            _, lang, code = code_blocks[block_id]

            if lang:
                xml_parts.append(indent(f'<code language="{lang}">', 2))
            else:
                xml_parts.append(indent("<code>", 2))

            # Add code with proper indentation
            for line in code.split("\n"):
                xml_parts.append(indent(escape_xml(line), 3))

            xml_parts.append(indent("</code>", 2))

    # Close content section
    xml_parts.append(indent("</content>", 1))

    # Close root element
    xml_parts.append(f"</{config.doc_tag}>")

    return "\n".join(xml_parts)


def convert_url_to_claude_xml(
    url_or_config: str | WebdownConfig,
    claude_xml_config: Optional[ClaudeXMLConfig] = None,
) -> str:
    """Convert a web page directly to Claude XML format.

    This function fetches a web page and converts it to Claude XML format,
    optimized for use with Claude AI models.

    Args:
        url_or_config (Union[str, WebdownConfig]): URL to fetch or config object
        claude_xml_config (Optional[ClaudeXMLConfig]): XML output configuration

    Returns:
        str: Claude XML formatted content

    Raises:
        WebdownError: If URL is invalid or cannot be fetched
    """
    # Determine the source URL
    source_url = None
    if isinstance(url_or_config, WebdownConfig):
        source_url = url_or_config.url
    else:
        source_url = url_or_config

    # Use the existing markdown conversion pipeline
    markdown = convert_url_to_markdown(url_or_config)

    # Convert the markdown to Claude XML
    return markdown_to_claude_xml(markdown, source_url, claude_xml_config)


def convert_url_to_markdown(
    url_or_config: str | WebdownConfig,
    include_links: bool = True,
    include_images: bool = True,
    include_toc: bool = False,
    css_selector: Optional[str] = None,
    compact_output: bool = False,
    body_width: int = 0,
    show_progress: bool = False,
) -> str:
    """Convert a web page to markdown.

    This function accepts either a URL string or a WebdownConfig object.
    If a URL string is provided, the remaining parameters are used for configuration.
    If a WebdownConfig object is provided, all other parameters are ignored.

    For large web pages (over 10MB), streaming mode is automatically used to
    optimize memory usage.

    Args:
        url_or_config (Union[str, WebdownConfig]):
            URL of the web page or a WebdownConfig object

        include_links (bool):
            Whether to include hyperlinks (ignored if config provided)

        include_images (bool):
            Whether to include images (ignored if config provided)

        include_toc (bool):
            Generate table of contents (ignored if config provided)

        css_selector (Optional[str]):
            CSS selector for extraction (ignored if config provided)

        compact_output (bool):
            Whether to remove blank lines (ignored if config provided)

        body_width (int):
            Maximum line length for text wrapping (ignored if config provided)

        show_progress (bool):
            Whether to display a progress bar (ignored if config provided)

    Returns:
        str: Markdown content

    Raises:
        WebdownError: If URL is invalid or cannot be fetched

    Examples:
        # Using individual parameters (backward compatible)
        markdown = convert_url_to_markdown(
            "https://example.com",
            include_toc=True,
            show_progress=True
        )

        # Using config object (new approach)
        config = WebdownConfig(
            url="https://example.com",
            include_toc=True,
            show_progress=True
        )
        markdown = convert_url_to_markdown(config)
    """
    # Determine if we're using a config object or URL string
    if isinstance(url_or_config, WebdownConfig):
        config = url_or_config
        if config.url is None:
            raise WebdownError("URL must be provided in the config object")
        url = config.url
        include_links = config.include_links
        include_images = config.include_images
        include_toc = config.include_toc
        css_selector = config.css_selector
        compact_output = config.compact_output
        body_width = config.body_width
        show_progress = config.show_progress
    else:
        # Using the traditional parameter-based approach
        url = url_or_config
        config = None

    # Validate URL
    if not validate_url(url):
        raise WebdownError(f"Invalid URL format: {url}")

    # Fixed streaming threshold at 10MB
    STREAM_THRESHOLD = 10 * 1024 * 1024

    try:
        # Check content length with a HEAD request to determine if we should stream
        use_streaming = False
        try:
            head_response = requests.head(url, timeout=5)
            content_length = int(head_response.headers.get("content-length", "0"))
            use_streaming = content_length > STREAM_THRESHOLD
        except (requests.RequestException, ValueError):
            # If HEAD request fails or content-length is invalid, use non-streaming
            use_streaming = False

        if use_streaming:
            # Use streaming mode for large documents
            return _process_url_streaming(
                url,
                include_links=include_links,
                include_images=include_images,
                include_toc=include_toc,
                css_selector=css_selector,
                compact_output=compact_output,
                body_width=body_width,
                show_progress=show_progress,
                config=config,
            )
        else:
            # Use standard mode for smaller documents
            html = fetch_url(url, show_progress=show_progress)

            if config is not None:
                # Pass the config object to html_to_markdown
                return html_to_markdown(html, config=config)
            else:
                # Use individual parameters
                return html_to_markdown(
                    html,
                    include_links=include_links,
                    include_images=include_images,
                    include_toc=include_toc,
                    css_selector=css_selector,
                    compact_output=compact_output,
                    body_width=body_width,
                )
    except requests.exceptions.Timeout:
        raise WebdownError(f"Connection timed out while fetching {url}")
    except requests.exceptions.ConnectionError:
        raise WebdownError(f"Connection error while fetching {url}")
    except requests.exceptions.HTTPError as e:
        raise WebdownError(f"HTTP error {e.response.status_code} while fetching {url}")
    except requests.exceptions.RequestException as e:
        raise WebdownError(f"Error fetching {url}: {str(e)}")


def _process_url_streaming(
    url: str,
    include_links: bool = True,
    include_images: bool = True,
    include_toc: bool = False,
    css_selector: Optional[str] = None,
    compact_output: bool = False,
    body_width: int = 0,
    show_progress: bool = False,
    config: Optional[WebdownConfig] = None,
) -> str:
    """Process a URL using streaming mode for large documents.

    This internal function handles large documents by streaming the content
    and processing it in chunks to minimize memory usage. It is automatically
    used for documents larger than 10MB to optimize memory usage.

    Args:
        url: URL to fetch and process
        Other parameters: Same as convert_url_to_markdown

    Returns:
        str: Markdown content
    """
    # Make a streaming request
    response = requests.get(url, timeout=10, stream=True)
    response.raise_for_status()

    # Get content length if available
    total_size = int(response.headers.get("content-length", 0))

    # Create a buffer for the HTML content
    html_buffer = io.StringIO()

    # Create progress bar if requested
    progress_desc = f"Downloading {url.split('/')[-1] or 'webpage'}"
    with tqdm(
        total=total_size if total_size > 0 else None,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
        desc=progress_desc,
        disable=not show_progress,
    ) as progress_bar:
        # Process content in chunks
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                # Calculate chunk size for progress bar
                if isinstance(chunk, bytes):
                    chunk_size = len(chunk)
                    text_chunk = chunk.decode("utf-8", errors="replace")
                else:
                    chunk_size = len(chunk.encode("utf-8"))
                    text_chunk = chunk

                # Update progress
                progress_bar.update(chunk_size)

                # Append to buffer
                html_buffer.write(text_chunk)

    # Get complete HTML content
    html = html_buffer.getvalue()

    # Process with html_to_markdown
    if config is not None:
        return html_to_markdown(html, config=config)
    else:
        return html_to_markdown(
            html,
            include_links=include_links,
            include_images=include_images,
            include_toc=include_toc,
            css_selector=css_selector,
            compact_output=compact_output,
            body_width=body_width,
        )
