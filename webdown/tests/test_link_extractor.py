"""Tests for the link_extractor module."""

import pytest

from webdown.config import WebdownError
from webdown.link_extractor import (
    ScopeType,
    _get_base_domain,
    extract_links,
    filter_links_by_scope,
    get_url_depth,
    is_same_domain,
    normalize_url,
    parse_sitemap,
)


class TestExtractLinks:
    """Tests for extract_links function."""

    def test_extract_absolute_links(self) -> None:
        """Test extracting absolute URLs from HTML."""
        html = """
        <html>
        <body>
            <a href="https://example.com/page1">Page 1</a>
            <a href="https://example.com/page2">Page 2</a>
        </body>
        </html>
        """
        links = extract_links(html, "https://example.com/")
        assert "https://example.com/page1" in links
        assert "https://example.com/page2" in links

    def test_extract_relative_links(self) -> None:
        """Test extracting and resolving relative URLs."""
        html = """
        <html>
        <body>
            <a href="/page1">Page 1</a>
            <a href="page2">Page 2</a>
            <a href="../parent">Parent</a>
        </body>
        </html>
        """
        links = extract_links(html, "https://example.com/docs/")
        assert "https://example.com/page1" in links
        assert "https://example.com/docs/page2" in links
        assert "https://example.com/parent" in links

    def test_skip_javascript_links(self) -> None:
        """Test that javascript: links are skipped."""
        html = '<a href="javascript:void(0)">Click</a>'
        links = extract_links(html, "https://example.com/")
        assert len(links) == 0

    def test_skip_mailto_links(self) -> None:
        """Test that mailto: links are skipped."""
        html = '<a href="mailto:test@example.com">Email</a>'
        links = extract_links(html, "https://example.com/")
        assert len(links) == 0

    def test_skip_tel_links(self) -> None:
        """Test that tel: links are skipped."""
        html = '<a href="tel:+1234567890">Call</a>'
        links = extract_links(html, "https://example.com/")
        assert len(links) == 0

    def test_skip_fragment_only_links(self) -> None:
        """Test that fragment-only links are skipped."""
        html = '<a href="#section">Section</a>'
        links = extract_links(html, "https://example.com/")
        assert len(links) == 0

    def test_skip_empty_href(self) -> None:
        """Test that empty href is skipped."""
        html = '<a href="">Empty</a>'
        links = extract_links(html, "https://example.com/")
        assert len(links) == 0

    def test_only_http_https(self) -> None:
        """Test that only http/https links are extracted."""
        html = """
        <a href="https://example.com/secure">HTTPS</a>
        <a href="http://example.com/plain">HTTP</a>
        <a href="ftp://example.com/file">FTP</a>
        """
        links = extract_links(html, "https://example.com/")
        assert "https://example.com/secure" in links
        assert "http://example.com/plain" in links
        assert "ftp://example.com/file" not in links


class TestNormalizeUrl:
    """Tests for normalize_url function."""

    def test_lowercase_scheme_and_domain(self) -> None:
        """Test that scheme and domain are lowercased."""
        url = normalize_url("HTTPS://EXAMPLE.COM/Page")
        assert url == "https://example.com/Page"

    def test_remove_fragment(self) -> None:
        """Test that fragments are removed."""
        url = normalize_url("https://example.com/page#section")
        assert url == "https://example.com/page"

    def test_remove_trailing_slash(self) -> None:
        """Test that trailing slashes are removed (except root)."""
        url = normalize_url("https://example.com/page/")
        assert url == "https://example.com/page"

    def test_keep_root_slash(self) -> None:
        """Test that root path keeps its slash."""
        url = normalize_url("https://example.com/")
        assert url == "https://example.com/"

    def test_add_root_slash_if_missing(self) -> None:
        """Test that root path is added if missing."""
        url = normalize_url("https://example.com")
        assert url == "https://example.com/"

    def test_keep_query_params(self) -> None:
        """Test that query parameters are preserved."""
        url = normalize_url("https://example.com/page?foo=bar")
        assert url == "https://example.com/page?foo=bar"


class TestFilterLinksByScope:
    """Tests for filter_links_by_scope function."""

    def test_same_subdomain_scope(self) -> None:
        """Test filtering by same subdomain."""
        links = [
            "https://docs.example.com/page1",
            "https://docs.example.com/page2",
            "https://api.example.com/endpoint",
            "https://example.com/home",
        ]
        filtered = filter_links_by_scope(
            links, "https://docs.example.com/", ScopeType.SAME_SUBDOMAIN
        )
        assert len(filtered) == 2
        assert "https://docs.example.com/page1" in filtered
        assert "https://docs.example.com/page2" in filtered

    def test_same_domain_scope(self) -> None:
        """Test filtering by same domain."""
        links = [
            "https://docs.example.com/page1",
            "https://api.example.com/endpoint",
            "https://other.org/page",
        ]
        filtered = filter_links_by_scope(
            links, "https://docs.example.com/", ScopeType.SAME_DOMAIN
        )
        assert len(filtered) == 2
        assert "https://docs.example.com/page1" in filtered
        assert "https://api.example.com/endpoint" in filtered

    def test_path_prefix_scope(self) -> None:
        """Test filtering by path prefix."""
        links = [
            "https://example.com/docs/page1",
            "https://example.com/docs/guide/intro",
            "https://example.com/api/endpoint",
            "https://example.com/about",
        ]
        filtered = filter_links_by_scope(
            links,
            "https://example.com/docs/",
            ScopeType.PATH_PREFIX,
            path_prefix="/docs/",
        )
        assert len(filtered) == 2
        assert "https://example.com/docs/page1" in filtered
        assert "https://example.com/docs/guide/intro" in filtered

    def test_path_prefix_with_seed_url(self) -> None:
        """Test path prefix derived from seed URL."""
        links = [
            "https://example.com/docs/page1",
            "https://example.com/docs/guide/intro",
            "https://example.com/api/endpoint",
        ]
        filtered = filter_links_by_scope(
            links,
            "https://example.com/docs/intro",
            ScopeType.PATH_PREFIX,
        )
        assert len(filtered) == 2


class TestGetBaseDomain:
    """Tests for _get_base_domain function."""

    def test_simple_domain(self) -> None:
        """Test simple two-part domain."""
        assert _get_base_domain("example.com") == "example.com"

    def test_subdomain(self) -> None:
        """Test domain with subdomain."""
        assert _get_base_domain("docs.example.com") == "example.com"

    def test_deep_subdomain(self) -> None:
        """Test domain with multiple subdomains."""
        assert _get_base_domain("api.docs.example.com") == "example.com"

    def test_with_port(self) -> None:
        """Test domain with port number."""
        assert _get_base_domain("example.com:8080") == "example.com"


class TestIsSameDomain:
    """Tests for is_same_domain function."""

    def test_same_domain(self) -> None:
        """Test URLs with same domain."""
        assert is_same_domain(
            "https://docs.example.com/page", "https://api.example.com/endpoint"
        )

    def test_different_domain(self) -> None:
        """Test URLs with different domains."""
        assert not is_same_domain("https://example.com/page", "https://other.org/page")


class TestGetUrlDepth:
    """Tests for get_url_depth function."""

    def test_same_level(self) -> None:
        """Test URL at same level as base."""
        depth = get_url_depth(
            "https://example.com/docs/page1", "https://example.com/docs/"
        )
        assert depth == 1

    def test_deeper_level(self) -> None:
        """Test URL deeper than base."""
        depth = get_url_depth(
            "https://example.com/docs/guide/intro", "https://example.com/docs/"
        )
        assert depth == 2

    def test_root_base(self) -> None:
        """Test with root as base."""
        depth = get_url_depth("https://example.com/docs/page", "https://example.com/")
        assert depth == 2


class TestParseSitemap:
    """Tests for parse_sitemap function."""

    def test_parse_sitemap_error_handling(  # type: ignore[no-untyped-def]
        self, requests_mock
    ) -> None:
        """Test error handling for invalid sitemap."""
        requests_mock.get(
            "https://example.com/sitemap.xml",
            status_code=404,
        )
        with pytest.raises(WebdownError):
            parse_sitemap("https://example.com/sitemap.xml")

    def test_parse_valid_sitemap(  # type: ignore[no-untyped-def]
        self, requests_mock
    ) -> None:
        """Test parsing a valid sitemap."""
        sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>https://example.com/page1</loc>
            </url>
            <url>
                <loc>https://example.com/page2</loc>
            </url>
        </urlset>
        """
        requests_mock.get(
            "https://example.com/sitemap.xml",
            text=sitemap_content,
        )
        urls = parse_sitemap("https://example.com/sitemap.xml")
        assert len(urls) == 2
        assert "https://example.com/page1" in urls
        assert "https://example.com/page2" in urls

    def test_parse_invalid_xml(  # type: ignore[no-untyped-def]
        self, requests_mock
    ) -> None:
        """Test error handling for malformed XML."""
        requests_mock.get(
            "https://example.com/sitemap.xml",
            text="not valid xml",
        )
        with pytest.raises(WebdownError):
            parse_sitemap("https://example.com/sitemap.xml")
