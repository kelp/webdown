"""Web crawler for converting multiple pages to Markdown or Claude XML.

This module provides the core crawling functionality for webdown, allowing
users to crawl multiple pages from a website and convert them to Markdown
or Claude XML format.
"""

import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime

from webdown.config import OutputFormat, WebdownConfig, WebdownError
from webdown.converter import convert_url
from webdown.link_extractor import (
    ScopeType,
    extract_links,
    filter_links_by_scope,
    normalize_url,
    parse_sitemap,
)
from webdown.output_manager import (
    CrawledPage,
    CrawlResult,
    get_relative_path,
    url_to_filepath,
    write_manifest,
    write_output_file,
)
from webdown.xml_converter import extract_markdown_title


@dataclass
class CrawlerConfig:
    """Configuration for web crawling.

    Attributes:
        seed_urls: List of URLs to start crawling from.
        output_dir: Directory to save converted files.
        max_depth: Maximum link depth from seed URLs (default: 3).
        delay_seconds: Delay between requests in seconds (default: 1.0).
        scope: Type of scope filtering to apply (default: SAME_SUBDOMAIN).
        path_prefix: Optional path prefix for PATH_PREFIX scope.
        conversion_config: Configuration for page conversion.
        verbose: Whether to print progress messages.
        max_pages: Maximum number of pages to crawl (0 for unlimited).
    """

    seed_urls: list[str]
    output_dir: str
    max_depth: int = 3
    delay_seconds: float = 1.0
    scope: ScopeType = ScopeType.SAME_SUBDOMAIN
    path_prefix: str | None = None
    conversion_config: WebdownConfig = field(default_factory=WebdownConfig)
    verbose: bool = True
    max_pages: int = 0


def crawl(config: CrawlerConfig) -> CrawlResult:
    """Execute a crawl operation starting from seed URLs.

    Uses breadth-first search to discover and convert pages within the
    configured scope. Respects rate limiting with configurable delays
    between requests.

    Args:
        config: Configuration for the crawl operation.

    Returns:
        CrawlResult containing metadata for all crawled pages.

    Raises:
        WebdownError: If the output directory cannot be created or accessed.
    """
    result = CrawlResult(
        start_time=datetime.now(),
        seed_urls=config.seed_urls.copy(),
        max_depth=config.max_depth,
        output_format=config.conversion_config.format.name.lower(),
    )

    visited: set[str] = set()
    queue: deque[tuple[str, int]] = deque()

    for seed_url in config.seed_urls:
        normalized = normalize_url(seed_url)
        if normalized not in visited:
            queue.append((seed_url, 0))
            visited.add(normalized)

    pages_crawled = 0

    while queue:
        if config.max_pages > 0 and pages_crawled >= config.max_pages:
            if config.verbose:
                print(f"Reached maximum page limit ({config.max_pages})")
            break

        url, depth = queue.popleft()

        if depth > config.max_depth:
            continue

        page = _crawl_single_page(url, depth, config, result)
        result.pages.append(page)
        pages_crawled += 1

        if config.verbose:
            status_char = "+" if page.status == "success" else "!"
            print(f"[{status_char}] {url}")

        if page.status == "success" and depth < config.max_depth:
            new_links = _discover_links(url, page, config, visited)
            for link in new_links:
                queue.append((link, depth + 1))

        if queue and config.delay_seconds > 0:
            time.sleep(config.delay_seconds)

    result.end_time = datetime.now()

    manifest_path = write_manifest(result, config.output_dir)
    if config.verbose:
        print(f"\nCrawl complete: {result.successful_count} pages saved")
        print(f"Manifest written to: {manifest_path}")

    return result


def _crawl_single_page(
    url: str,
    depth: int,
    config: CrawlerConfig,
    result: CrawlResult,
) -> CrawledPage:
    """Crawl and convert a single page.

    Args:
        url: The URL to crawl.
        depth: The current crawl depth.
        config: The crawler configuration.
        result: The crawl result to update.

    Returns:
        CrawledPage with the crawl metadata.
    """
    output_path = url_to_filepath(
        url, config.output_dir, config.conversion_config.format
    )
    relative_path = get_relative_path(output_path, config.output_dir)

    try:
        page_config = WebdownConfig(
            url=url,
            css_selector=config.conversion_config.css_selector,
            include_links=config.conversion_config.include_links,
            include_images=config.conversion_config.include_images,
            format=config.conversion_config.format,
            document_options=config.conversion_config.document_options,
            show_progress=False,
        )

        content = convert_url(page_config)

        title = None
        if config.conversion_config.format == OutputFormat.MARKDOWN:
            title = extract_markdown_title(content)
        elif config.conversion_config.format == OutputFormat.CLAUDE_XML:
            title = _extract_xml_title(content)

        write_output_file(output_path, content)

        return CrawledPage(
            url=url,
            output_path=relative_path,
            title=title,
            crawled_at=datetime.now(),
            depth=depth,
            status="success",
        )

    except WebdownError as e:
        return CrawledPage(
            url=url,
            output_path=relative_path,
            title=None,
            crawled_at=datetime.now(),
            depth=depth,
            status="error",
            error_message=str(e),
        )
    except Exception as e:
        return CrawledPage(
            url=url,
            output_path=relative_path,
            title=None,
            crawled_at=datetime.now(),
            depth=depth,
            status="error",
            error_message=f"Unexpected error: {e}",
        )


def _discover_links(
    url: str,
    page: CrawledPage,
    config: CrawlerConfig,
    visited: set[str],
) -> list[str]:
    """Discover new links from a crawled page.

    Args:
        url: The URL that was crawled.
        page: The crawled page metadata.
        config: The crawler configuration.
        visited: Set of already-visited normalized URLs.

    Returns:
        List of new URLs to crawl.
    """
    try:
        from webdown.html_parser import fetch_url

        html = fetch_url(url, show_progress=False)
    except Exception:
        return []

    all_links = extract_links(html, url)

    seed_url = config.seed_urls[0] if config.seed_urls else url
    filtered_links = filter_links_by_scope(
        all_links,
        seed_url,
        config.scope,
        config.path_prefix,
    )

    new_links = []
    for link in filtered_links:
        normalized = normalize_url(link)
        if normalized not in visited:
            visited.add(normalized)
            new_links.append(link)

    return new_links


def _extract_xml_title(content: str) -> str | None:
    """Extract the title from Claude XML content.

    Args:
        content: The Claude XML content.

    Returns:
        The title if found, None otherwise.
    """
    import re

    match = re.search(r"<title>([^<]+)</title>", content)
    return match.group(1) if match else None


def crawl_from_sitemap(
    sitemap_url: str,
    config: CrawlerConfig,
) -> CrawlResult:
    """Crawl pages listed in a sitemap.xml file.

    Instead of following links, this function parses a sitemap and
    converts all URLs listed in it.

    Args:
        sitemap_url: URL of the sitemap.xml file.
        config: Configuration for the crawl operation.

    Returns:
        CrawlResult containing metadata for all crawled pages.

    Raises:
        WebdownError: If the sitemap cannot be fetched or parsed.
    """
    result = CrawlResult(
        start_time=datetime.now(),
        seed_urls=[sitemap_url],
        max_depth=0,
        output_format=config.conversion_config.format.name.lower(),
    )

    if config.verbose:
        print(f"Parsing sitemap: {sitemap_url}")

    urls = parse_sitemap(sitemap_url)

    if config.verbose:
        print(f"Found {len(urls)} URLs in sitemap")

    if config.scope != ScopeType.SAME_DOMAIN:
        seed_url = config.seed_urls[0] if config.seed_urls else sitemap_url
        urls = filter_links_by_scope(
            urls,
            seed_url,
            config.scope,
            config.path_prefix,
        )
        if config.verbose:
            print(f"After scope filtering: {len(urls)} URLs")

    pages_crawled = 0

    for url in urls:
        if config.max_pages > 0 and pages_crawled >= config.max_pages:
            if config.verbose:
                print(f"Reached maximum page limit ({config.max_pages})")
            break

        page = _crawl_single_page(url, 0, config, result)
        result.pages.append(page)
        pages_crawled += 1

        if config.verbose:
            status_char = "+" if page.status == "success" else "!"
            print(f"[{status_char}] {url}")

        if pages_crawled < len(urls) and config.delay_seconds > 0:
            time.sleep(config.delay_seconds)

    result.end_time = datetime.now()

    manifest_path = write_manifest(result, config.output_dir)
    if config.verbose:
        print(f"\nCrawl complete: {result.successful_count} pages saved")
        print(f"Manifest written to: {manifest_path}")

    return result
