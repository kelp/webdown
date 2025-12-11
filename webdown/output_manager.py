"""Output file management for the crawler.

This module handles converting URLs to file paths, managing the output
directory structure, and writing the crawl manifest (index.json).
"""

import json
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from webdown.config import OutputFormat


@dataclass
class CrawledPage:
    """Metadata for a crawled page.

    Attributes:
        url: The original URL that was crawled.
        output_path: Relative path to the output file from the output directory.
        title: The page title extracted from the content, if available.
        crawled_at: Timestamp when the page was crawled.
        depth: The crawl depth from the seed URL (0 for seed URLs).
        status: The crawl status ("success", "error", or "skipped").
        error_message: Error message if status is "error", None otherwise.
    """

    url: str
    output_path: str
    title: str | None
    crawled_at: datetime
    depth: int
    status: str
    error_message: str | None = None


@dataclass
class CrawlResult:
    """Result of a crawl operation.

    Attributes:
        pages: List of all crawled pages with their metadata.
        start_time: When the crawl started.
        end_time: When the crawl completed.
        seed_urls: The original seed URLs used to start the crawl.
        max_depth: The maximum depth setting used.
        output_format: The output format used (markdown or claude_xml).
    """

    pages: list[CrawledPage] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime = field(default_factory=datetime.now)
    seed_urls: list[str] = field(default_factory=list)
    max_depth: int = 3
    output_format: str = "markdown"

    @property
    def successful_count(self) -> int:
        """Return the number of successfully crawled pages."""
        return sum(1 for p in self.pages if p.status == "success")

    @property
    def error_count(self) -> int:
        """Return the number of pages that failed to crawl."""
        return sum(1 for p in self.pages if p.status == "error")

    @property
    def skipped_count(self) -> int:
        """Return the number of skipped pages."""
        return sum(1 for p in self.pages if p.status == "skipped")


def url_to_filepath(
    url: str,
    output_dir: str,
    output_format: OutputFormat = OutputFormat.MARKDOWN,
) -> str:
    """Convert a URL to an output file path.

    Creates a path structure that mirrors the URL structure:
    - https://example.com/docs/page -> output_dir/example.com/docs/page.md
    - https://example.com/docs/ -> output_dir/example.com/docs/index.md
    - https://example.com/ -> output_dir/example.com/index.md

    Args:
        url: The URL to convert to a file path.
        output_dir: The base output directory.
        output_format: The output format (determines file extension).

    Returns:
        The full file path for the converted content.
    """
    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    if ":" in domain:
        domain = domain.replace(":", "_")

    path = parsed.path
    if not path or path == "/":
        path = "/index"
    elif path.endswith("/"):
        path = path + "index"

    path = path.lstrip("/")

    if path.endswith(".html") or path.endswith(".htm"):
        path = re.sub(r"\.html?$", "", path)

    path = _sanitize_path(path)

    extension = ".xml" if output_format == OutputFormat.CLAUDE_XML else ".md"

    full_path = os.path.join(output_dir, domain, path + extension)

    return full_path


def _sanitize_path(path: str) -> str:
    """Sanitize a path component for use in the filesystem.

    Args:
        path: The path to sanitize.

    Returns:
        A sanitized path safe for filesystem use.
    """
    path = re.sub(r'[<>:"|?*]', "_", path)

    parts = path.split("/")
    sanitized_parts = []
    for part in parts:
        part = part.strip()
        if part and part != "." and part != "..":
            if len(part) > 200:
                part = part[:200]
            sanitized_parts.append(part)

    return "/".join(sanitized_parts) if sanitized_parts else "index"


def get_relative_path(full_path: str, output_dir: str) -> str:
    """Get the relative path from the output directory.

    Args:
        full_path: The full file path.
        output_dir: The base output directory.

    Returns:
        The path relative to output_dir.
    """
    return os.path.relpath(full_path, output_dir)


def ensure_output_directory(filepath: str) -> None:
    """Ensure the directory for a file path exists.

    Args:
        filepath: The file path whose directory should be created.
    """
    directory = os.path.dirname(filepath)
    if directory:
        Path(directory).mkdir(parents=True, exist_ok=True)


def write_output_file(filepath: str, content: str) -> None:
    """Write content to a file, creating directories as needed.

    Args:
        filepath: The path to write to.
        content: The content to write.
    """
    ensure_output_directory(filepath)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def write_manifest(result: CrawlResult, output_dir: str) -> str:
    """Write the crawl manifest (index.json) to the output directory.

    Args:
        result: The crawl result containing all page metadata.
        output_dir: The output directory to write the manifest to.

    Returns:
        The path to the written manifest file.
    """
    manifest = {
        "version": "1.0",
        "crawl_info": {
            "seed_urls": result.seed_urls,
            "start_time": result.start_time.isoformat(),
            "end_time": result.end_time.isoformat(),
            "total_pages": len(result.pages),
            "successful": result.successful_count,
            "errors": result.error_count,
            "skipped": result.skipped_count,
            "max_depth": result.max_depth,
            "output_format": result.output_format,
        },
        "pages": [_page_to_dict(page) for page in result.pages],
    }

    manifest_path = os.path.join(output_dir, "index.json")
    ensure_output_directory(manifest_path)

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    return manifest_path


def _page_to_dict(page: CrawledPage) -> dict:
    """Convert a CrawledPage to a dictionary for JSON serialization.

    Args:
        page: The page to convert.

    Returns:
        A dictionary representation of the page.
    """
    d = asdict(page)
    d["crawled_at"] = page.crawled_at.isoformat()
    return d
