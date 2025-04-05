"""HTML to Markdown and Claude XML conversion functionality.

This module serves as the main entry point for the webdown package, providing
the primary functions for converting web content to Markdown and Claude XML formats.

The conversion process involves multiple steps:
1. Fetch or read HTML content (from URL or local file)
2. Convert HTML to Markdown
3. Optionally convert Markdown to Claude XML format

Key functions:
- convert_url: Convert web content to Markdown or XML
- convert_file: Convert local HTML file to Markdown or XML
"""

from webdown.config import DocumentOptions, OutputFormat, WebdownConfig, WebdownError
from webdown.html_parser import _check_streaming_needed, fetch_url, read_html_file
from webdown.markdown_converter import html_to_markdown
from webdown.validation import validate_css_selector, validate_url
from webdown.xml_converter import markdown_to_claude_xml

__all__ = [
    "WebdownConfig",
    "OutputFormat",
    "DocumentOptions",
    "WebdownError",
    "validate_url",
    "validate_css_selector",
    "fetch_url",
    "read_html_file",
    "html_to_markdown",
    "markdown_to_claude_xml",
    "convert_url",
    "convert_file",
]


def _validate_and_normalize_url_config(
    url_or_config: str | WebdownConfig,
) -> WebdownConfig:
    """Validate URL and normalize configuration into WebdownConfig object.

    This function centralizes URL validation logic for the entire converter module.
    All code paths that need a validated URL should go through this function.

    Args:
        url_or_config: URL string or WebdownConfig object. If a string is provided,
                      it will be used to create a WebdownConfig object.

    Returns:
        Normalized WebdownConfig with validated URL

    Raises:
        WebdownError: If URL is invalid or missing. Error code will be "URL_INVALID"
                     for format errors and "URL_MISSING" if no URL is provided.

    Examples:
        >>> config = _validate_and_normalize_url_config("https://example.com")
        >>> config.url
        'https://example.com'

        >>> existing = WebdownConfig(url="https://example.com")
        >>> config = _validate_and_normalize_url_config(existing)
        >>> config.url
        'https://example.com'
    """
    # Create config object if a URL string was provided
    if isinstance(url_or_config, str):
        config = WebdownConfig(url=url_or_config)
    else:
        config = url_or_config
        if config.url is None:
            raise WebdownError(
                "URL must be provided in the config object", code="URL_MISSING"
            )

    # At this point config.url cannot be None due to the check above
    url = config.url
    assert url is not None

    # Validate URL format - centralized validation for the entire module
    try:
        validate_url(url)
    except ValueError as e:
        raise WebdownError(str(e), code="URL_INVALID")

    return config


def _validate_and_normalize_file_config(
    file_path_or_config: str | WebdownConfig,
) -> WebdownConfig:
    """Validate file_path and normalize configuration into WebdownConfig object.

    This function centralizes file path validation for the converter module.
    All code paths that need a validated file path should use this function.

    Args:
        file_path_or_config: File path string or WebdownConfig object. If a string is
                            provided, a WebdownConfig object will be created.

    Returns:
        Normalized WebdownConfig with validated file_path

    Raises:
        WebdownError: If file_path is missing. Error code will be "FILE_MISSING".

    Examples:
        >>> config = _validate_and_normalize_file_config("page.html")
        >>> config.file_path
        'page.html'

        >>> existing = WebdownConfig(file_path="page.html")
        >>> config = _validate_and_normalize_file_config(existing)
        >>> config.file_path
        'page.html'
    """
    # Create config object if a file path string was provided
    if isinstance(file_path_or_config, str):
        config = WebdownConfig(file_path=file_path_or_config)
    else:
        config = file_path_or_config
        if config.file_path is None:
            raise WebdownError(
                "File path must be provided in the config object", code="FILE_MISSING"
            )

    # At this point config.file_path cannot be None due to the check above
    return config


def convert_url(url_or_config: str | WebdownConfig) -> str:
    """Convert a web page to the specified output format.

    This function accepts either a URL string or a WebdownConfig object.
    If a URL string is provided, it will be used to create a WebdownConfig object
    with default settings (Markdown output).

    For large web pages (over 10MB), streaming mode is automatically used.

    Args:
        url_or_config: URL of the web page or a WebdownConfig object

    Returns:
        Converted content in the format specified by config.format

    Raises:
        WebdownError: If URL is invalid or cannot be fetched

    Examples:
        # Basic usage with URL string (defaults to Markdown output)
        content = convert_url("https://example.com")

        # Using config object for Markdown output with Table of Contents
        doc_options = DocumentOptions(include_toc=True)
        config = WebdownConfig(
            url="https://example.com",
            show_progress=True,
            document_options=doc_options
        )
        content = convert_url(config)

        # Claude XML output
        config = WebdownConfig(
            url="https://example.com",
            format=OutputFormat.CLAUDE_XML
        )
        xml_content = convert_url(config)
    """
    # Get normalized config with validated URL
    config = _validate_and_normalize_url_config(url_or_config)
    # At this point, the URL has been validated and cannot be None
    url = config.url
    assert url is not None

    try:
        # Perform streaming check for large documents
        _check_streaming_needed(url)

        # Fetch the HTML content (URL already validated)
        html = fetch_url(url, show_progress=config.show_progress)

        # Convert HTML to Markdown
        markdown = html_to_markdown(html, config)

        # Convert to requested output format
        if config.format == OutputFormat.CLAUDE_XML:
            return markdown_to_claude_xml(
                markdown,
                source_url=url,
                include_metadata=config.document_options.include_metadata,
            )
        else:
            return markdown

    except Exception as e:
        # This is a fallback for any other request exceptions
        # Import error_utils here to avoid circular imports
        from webdown.error_utils import ErrorCode

        raise WebdownError(
            f"Error fetching {url}: {str(e)}", code=ErrorCode.UNEXPECTED_ERROR
        )


def convert_file(file_path_or_config: str | WebdownConfig) -> str:
    """Convert a local HTML file to the specified output format.

    This function accepts either a file path string or a WebdownConfig object.
    If a file path string is provided, it will be used to create a WebdownConfig object
    with default settings (Markdown output).

    Args:
        file_path_or_config: Path to the HTML file or a WebdownConfig object

    Returns:
        Converted content in the format specified by config.format

    Raises:
        WebdownError: If file cannot be read or processed

    Examples:
        # Basic usage with file path string (defaults to Markdown output)
        content = convert_file("page.html")

        # Using config object for Markdown output with Table of Contents
        doc_options = DocumentOptions(include_toc=True)
        config = WebdownConfig(
            file_path="page.html",
            document_options=doc_options
        )
        content = convert_file(config)

        # Claude XML output
        config = WebdownConfig(
            file_path="page.html",
            format=OutputFormat.CLAUDE_XML
        )
        xml_content = convert_file(config)
    """
    # Get normalized config with validated file_path
    config = _validate_and_normalize_file_config(file_path_or_config)
    # At this point, the file_path has been validated and cannot be None
    file_path = config.file_path
    assert file_path is not None

    try:
        # Read the HTML content from the file
        html = read_html_file(file_path)

        # Convert HTML to Markdown
        markdown = html_to_markdown(html, config)

        # Convert to requested output format
        if config.format == OutputFormat.CLAUDE_XML:
            return markdown_to_claude_xml(
                markdown,
                source_url=None,  # No URL for local files
                include_metadata=config.document_options.include_metadata,
            )
        else:
            return markdown

    except Exception as e:
        # If exception is a WebdownError (from read_html_file), just re-raise it
        if isinstance(e, WebdownError):
            raise

        # This is a fallback for any other exception
        from webdown.error_utils import ErrorCode

        raise WebdownError(
            f"Error processing file {file_path}: {str(e)}",
            code=ErrorCode.UNEXPECTED_ERROR,
        )
