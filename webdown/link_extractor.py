"""Link extraction and URL handling utilities for the crawler.

This module provides functions for extracting links from HTML content,
normalizing URLs for deduplication, filtering links by scope, and
parsing sitemap.xml files.
"""

import xml.etree.ElementTree as ET
from enum import Enum, auto
from urllib.parse import urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup

from webdown.config import WebdownError
from webdown.error_utils import ErrorCode


class ScopeType(Enum):
    """Enumeration of crawl scope types."""

    SAME_DOMAIN = auto()
    SAME_SUBDOMAIN = auto()
    PATH_PREFIX = auto()


def extract_links(html: str, base_url: str) -> list[str]:
    """Extract and resolve all links from HTML content.

    Finds all <a href="..."> links in the HTML and resolves them
    to absolute URLs using the base URL.

    Args:
        html: The HTML content to extract links from.
        base_url: The base URL for resolving relative links.

    Returns:
        A list of absolute URLs found in the HTML.
    """
    soup = BeautifulSoup(html, "html.parser")
    links: list[str] = []

    for anchor in soup.find_all("a", href=True):
        href = anchor.get("href", "")
        if not isinstance(href, str):
            continue
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue

        absolute_url = urljoin(base_url, href)
        parsed = urlparse(absolute_url)

        if parsed.scheme in ("http", "https"):
            links.append(absolute_url)

    return links


def normalize_url(url: str) -> str:
    """Normalize a URL for deduplication.

    Normalization includes:
    - Lowercasing the scheme and domain
    - Removing fragments (#anchor)
    - Removing trailing slashes (except for root paths)
    - Sorting and keeping query parameters

    Args:
        url: The URL to normalize.

    Returns:
        The normalized URL string.
    """
    parsed = urlparse(url)

    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path

    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")

    if not path:
        path = "/"

    normalized = urlunparse((scheme, netloc, path, parsed.params, parsed.query, ""))

    return normalized


def filter_links_by_scope(
    links: list[str],
    seed_url: str,
    scope: ScopeType,
    path_prefix: str | None = None,
) -> list[str]:
    """Filter links to only those within the configured scope.

    Args:
        links: List of URLs to filter.
        seed_url: The original seed URL used to determine scope.
        scope: The type of scope filtering to apply.
        path_prefix: Optional path prefix for PATH_PREFIX scope.

    Returns:
        Filtered list of URLs that match the scope criteria.
    """
    seed_parsed = urlparse(seed_url)
    filtered: list[str] = []

    for link in links:
        link_parsed = urlparse(link)

        if scope == ScopeType.SAME_DOMAIN:
            seed_domain = _get_base_domain(seed_parsed.netloc)
            link_domain = _get_base_domain(link_parsed.netloc)
            if seed_domain == link_domain:
                filtered.append(link)

        elif scope == ScopeType.SAME_SUBDOMAIN:
            if seed_parsed.netloc.lower() == link_parsed.netloc.lower():
                filtered.append(link)

        elif scope == ScopeType.PATH_PREFIX:
            if seed_parsed.netloc.lower() != link_parsed.netloc.lower():
                continue

            prefix = path_prefix if path_prefix else seed_parsed.path
            if not prefix.endswith("/"):
                prefix = prefix.rsplit("/", 1)[0] + "/"

            if link_parsed.path.startswith(prefix) or link_parsed.path == prefix.rstrip(
                "/"
            ):
                filtered.append(link)

    return filtered


def _get_base_domain(netloc: str) -> str:
    """Extract the base domain from a netloc (e.g., example.com from sub.example.com).

    Args:
        netloc: The network location (domain) string.

    Returns:
        The base domain (last two parts for most TLDs).
    """
    netloc = netloc.lower()
    if ":" in netloc:
        netloc = netloc.split(":")[0]

    parts = netloc.split(".")
    if len(parts) <= 2:
        return netloc

    return ".".join(parts[-2:])


def parse_sitemap(sitemap_url: str, timeout: int = 30) -> list[str]:
    """Parse a sitemap.xml file and return the list of URLs.

    Supports standard sitemap.xml format with <url><loc> elements.
    Also handles sitemap index files that reference other sitemaps.

    Args:
        sitemap_url: URL of the sitemap.xml file.
        timeout: Request timeout in seconds.

    Returns:
        List of URLs found in the sitemap.

    Raises:
        WebdownError: If the sitemap cannot be fetched or parsed.
    """
    try:
        response = requests.get(sitemap_url, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as e:
        raise WebdownError(
            f"Failed to fetch sitemap: {e}",
            ErrorCode.SITEMAP_PARSE_ERROR,
        ) from e

    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        raise WebdownError(
            f"Failed to parse sitemap XML: {e}",
            ErrorCode.SITEMAP_PARSE_ERROR,
        ) from e

    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls: list[str] = []

    sitemap_refs = root.findall(".//sm:sitemap/sm:loc", ns)
    if sitemap_refs:
        for sitemap_ref in sitemap_refs:
            if sitemap_ref.text:
                child_urls = parse_sitemap(sitemap_ref.text, timeout)
                urls.extend(child_urls)
    else:
        for loc in root.findall(".//sm:url/sm:loc", ns):
            if loc.text:
                urls.append(loc.text.strip())

        if not urls:
            for loc in root.findall(".//url/loc"):
                if loc.text:
                    urls.append(loc.text.strip())
            for loc in root.findall(".//loc"):
                if loc.text and loc.text.strip().startswith("http"):
                    urls.append(loc.text.strip())

    return urls


def is_same_domain(url1: str, url2: str) -> bool:
    """Check if two URLs share the same domain.

    Args:
        url1: First URL to compare.
        url2: Second URL to compare.

    Returns:
        True if both URLs have the same base domain.
    """
    parsed1 = urlparse(url1)
    parsed2 = urlparse(url2)
    return _get_base_domain(parsed1.netloc) == _get_base_domain(parsed2.netloc)


def get_url_depth(url: str, base_url: str) -> int:
    """Calculate the path depth of a URL relative to a base URL.

    Args:
        url: The URL to calculate depth for.
        base_url: The base URL to calculate depth from.

    Returns:
        The number of path segments deeper than the base URL.
    """
    url_parsed = urlparse(url)
    base_parsed = urlparse(base_url)

    url_path = url_parsed.path.strip("/")
    base_path = base_parsed.path.strip("/")

    url_parts = [p for p in url_path.split("/") if p]
    base_parts = [p for p in base_path.split("/") if p]

    if not base_parts:
        return len(url_parts)

    common = 0
    for i, part in enumerate(base_parts):
        if i < len(url_parts) and url_parts[i] == part:
            common += 1
        else:
            break

    return len(url_parts) - common
