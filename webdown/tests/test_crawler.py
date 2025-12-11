"""Tests for the crawler module."""

import os
import tempfile

from webdown.crawler import (
    CrawlerConfig,
    _crawl_single_page,
    _extract_xml_title,
    crawl,
    crawl_from_sitemap,
)
from webdown.link_extractor import ScopeType
from webdown.output_manager import CrawlResult


class TestCrawlerConfig:
    """Tests for CrawlerConfig dataclass."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = CrawlerConfig(
            seed_urls=["https://example.com/"],
            output_dir="/output",
        )
        assert config.max_depth == 3
        assert config.delay_seconds == 1.0
        assert config.scope == ScopeType.SAME_SUBDOMAIN
        assert config.path_prefix is None
        assert config.verbose is True
        assert config.max_pages == 0

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = CrawlerConfig(
            seed_urls=["https://example.com/"],
            output_dir="/output",
            max_depth=5,
            delay_seconds=2.0,
            scope=ScopeType.SAME_DOMAIN,
            path_prefix="/docs/",
            verbose=False,
            max_pages=100,
        )
        assert config.max_depth == 5
        assert config.delay_seconds == 2.0
        assert config.scope == ScopeType.SAME_DOMAIN
        assert config.path_prefix == "/docs/"
        assert config.verbose is False
        assert config.max_pages == 100


class TestCrawl:
    """Tests for crawl function."""

    def test_crawl_single_page(  # type: ignore[no-untyped-def]
        self, requests_mock
    ) -> None:
        """Test crawling a single page with no links."""
        # Mock HEAD request for streaming check
        requests_mock.head("https://example.com/", headers={"content-length": "100"})
        requests_mock.get(
            "https://example.com/",
            text="<html><body><h1>Test</h1><p>Content</p></body></html>",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            config = CrawlerConfig(
                seed_urls=["https://example.com/"],
                output_dir=tmpdir,
                max_depth=0,
                delay_seconds=0,
                verbose=False,
            )
            result = crawl(config)

            assert result.successful_count == 1
            assert len(result.pages) == 1
            assert result.pages[0].status == "success"

            # Check output file exists
            output_path = os.path.join(tmpdir, "example.com", "index.md")
            assert os.path.exists(output_path)

            # Check manifest exists
            manifest_path = os.path.join(tmpdir, "index.json")
            assert os.path.exists(manifest_path)

    def test_crawl_with_links(  # type: ignore[no-untyped-def]
        self, requests_mock
    ) -> None:
        """Test crawling pages with links."""
        # Mock HEAD requests for streaming check
        requests_mock.head("https://example.com/", headers={"content-length": "100"})
        requests_mock.head(
            "https://example.com/page1", headers={"content-length": "100"}
        )
        requests_mock.head(
            "https://example.com/page2", headers={"content-length": "100"}
        )
        requests_mock.get(
            "https://example.com/",
            text="""<html><body>
                <h1>Home</h1>
                <a href="/page1">Page 1</a>
                <a href="/page2">Page 2</a>
            </body></html>""",
        )
        requests_mock.get(
            "https://example.com/page1",
            text="<html><body><h1>Page 1</h1></body></html>",
        )
        requests_mock.get(
            "https://example.com/page2",
            text="<html><body><h1>Page 2</h1></body></html>",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            config = CrawlerConfig(
                seed_urls=["https://example.com/"],
                output_dir=tmpdir,
                max_depth=1,
                delay_seconds=0,
                verbose=False,
            )
            result = crawl(config)

            assert result.successful_count == 3
            assert len(result.pages) == 3

    def test_crawl_respects_max_depth(  # type: ignore[no-untyped-def]
        self, requests_mock
    ) -> None:
        """Test that crawl respects max_depth setting."""
        # Mock HEAD requests
        requests_mock.head("https://example.com/", headers={"content-length": "100"})
        requests_mock.head(
            "https://example.com/level1", headers={"content-length": "100"}
        )
        requests_mock.head(
            "https://example.com/level2", headers={"content-length": "100"}
        )
        requests_mock.get(
            "https://example.com/",
            text='<html><body><a href="/level1">L1</a></body></html>',
        )
        requests_mock.get(
            "https://example.com/level1",
            text='<html><body><a href="/level2">L2</a></body></html>',
        )
        requests_mock.get(
            "https://example.com/level2",
            text="<html><body>Deep</body></html>",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            config = CrawlerConfig(
                seed_urls=["https://example.com/"],
                output_dir=tmpdir,
                max_depth=1,
                delay_seconds=0,
                verbose=False,
            )
            result = crawl(config)

            # Should only crawl root and level1, not level2
            urls = [p.url for p in result.pages]
            assert "https://example.com/" in urls
            assert "https://example.com/level1" in urls
            assert "https://example.com/level2" not in urls

    def test_crawl_respects_max_pages(  # type: ignore[no-untyped-def]
        self, requests_mock
    ) -> None:
        """Test that crawl respects max_pages setting."""
        # Mock HEAD requests
        requests_mock.head("https://example.com/", headers={"content-length": "100"})
        for i in range(1, 4):
            requests_mock.head(
                f"https://example.com/page{i}", headers={"content-length": "100"}
            )
        requests_mock.get(
            "https://example.com/",
            text="""<html><body>
                <a href="/page1">P1</a>
                <a href="/page2">P2</a>
                <a href="/page3">P3</a>
            </body></html>""",
        )
        for i in range(1, 4):
            requests_mock.get(
                f"https://example.com/page{i}",
                text=f"<html><body>Page {i}</body></html>",
            )

        with tempfile.TemporaryDirectory() as tmpdir:
            config = CrawlerConfig(
                seed_urls=["https://example.com/"],
                output_dir=tmpdir,
                max_depth=1,
                delay_seconds=0,
                verbose=False,
                max_pages=2,
            )
            result = crawl(config)

            assert len(result.pages) == 2

    def test_crawl_deduplicates_urls(  # type: ignore[no-untyped-def]
        self, requests_mock
    ) -> None:
        """Test that crawl doesn't visit the same URL twice."""
        # Mock HEAD requests
        requests_mock.head("https://example.com/", headers={"content-length": "100"})
        requests_mock.head(
            "https://example.com/page", headers={"content-length": "100"}
        )
        requests_mock.get(
            "https://example.com/",
            text="""<html><body>
                <a href="/page">Link 1</a>
                <a href="/page">Link 2</a>
                <a href="/page/">Link 3 with slash</a>
            </body></html>""",
        )
        requests_mock.get(
            "https://example.com/page",
            text="<html><body>Page</body></html>",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            config = CrawlerConfig(
                seed_urls=["https://example.com/"],
                output_dir=tmpdir,
                max_depth=1,
                delay_seconds=0,
                verbose=False,
            )
            result = crawl(config)

            # Should only crawl root and page once
            assert len(result.pages) == 2

    def test_crawl_handles_errors(  # type: ignore[no-untyped-def]
        self, requests_mock
    ) -> None:
        """Test that crawl handles page errors gracefully."""
        # Mock HEAD requests
        requests_mock.head("https://example.com/", headers={"content-length": "100"})
        requests_mock.head(
            "https://example.com/error", headers={"content-length": "100"}
        )
        requests_mock.get(
            "https://example.com/",
            text='<html><body><a href="/error">Error</a></body></html>',
        )
        requests_mock.get(
            "https://example.com/error",
            status_code=404,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            config = CrawlerConfig(
                seed_urls=["https://example.com/"],
                output_dir=tmpdir,
                max_depth=1,
                delay_seconds=0,
                verbose=False,
            )
            result = crawl(config)

            assert result.successful_count == 1
            assert result.error_count == 1


class TestCrawlFromSitemap:
    """Tests for crawl_from_sitemap function."""

    def test_crawl_from_sitemap(  # type: ignore[no-untyped-def]
        self, requests_mock
    ) -> None:
        """Test crawling pages from a sitemap."""
        sitemap = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url><loc>https://example.com/page1</loc></url>
            <url><loc>https://example.com/page2</loc></url>
        </urlset>
        """
        requests_mock.get("https://example.com/sitemap.xml", text=sitemap)
        # Mock HEAD requests
        requests_mock.head(
            "https://example.com/page1", headers={"content-length": "100"}
        )
        requests_mock.head(
            "https://example.com/page2", headers={"content-length": "100"}
        )
        requests_mock.get(
            "https://example.com/page1",
            text="<html><body><h1>Page 1</h1></body></html>",
        )
        requests_mock.get(
            "https://example.com/page2",
            text="<html><body><h1>Page 2</h1></body></html>",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            config = CrawlerConfig(
                seed_urls=[],
                output_dir=tmpdir,
                delay_seconds=0,
                verbose=False,
            )
            result = crawl_from_sitemap("https://example.com/sitemap.xml", config)

            assert result.successful_count == 2
            assert len(result.pages) == 2


class TestExtractXmlTitle:
    """Tests for _extract_xml_title function."""

    def test_extract_title(self) -> None:
        """Test extracting title from XML content."""
        content = "<document><title>Test Title</title><content>...</content></document>"
        assert _extract_xml_title(content) == "Test Title"

    def test_no_title(self) -> None:
        """Test handling content without title."""
        content = "<document><content>No title here</content></document>"
        assert _extract_xml_title(content) is None


class TestCrawlSinglePage:
    """Tests for _crawl_single_page function."""

    def test_successful_crawl(  # type: ignore[no-untyped-def]
        self, requests_mock
    ) -> None:
        """Test successful single page crawl."""
        # Mock HEAD request
        requests_mock.head(
            "https://example.com/page", headers={"content-length": "100"}
        )
        requests_mock.get(
            "https://example.com/page",
            text="<html><body><h1>Test</h1></body></html>",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            config = CrawlerConfig(
                seed_urls=["https://example.com/"],
                output_dir=tmpdir,
                verbose=False,
            )
            result = CrawlResult()

            page = _crawl_single_page(
                "https://example.com/page",
                0,
                config,
                result,
            )

            assert page.status == "success"
            assert page.depth == 0
            assert page.url == "https://example.com/page"

    def test_failed_crawl(self, requests_mock) -> None:  # type: ignore[no-untyped-def]
        """Test failed single page crawl."""
        # Mock HEAD request
        requests_mock.head(
            "https://example.com/error", headers={"content-length": "100"}
        )
        requests_mock.get(
            "https://example.com/error",
            status_code=500,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            config = CrawlerConfig(
                seed_urls=["https://example.com/"],
                output_dir=tmpdir,
                verbose=False,
            )
            result = CrawlResult()

            page = _crawl_single_page(
                "https://example.com/error",
                0,
                config,
                result,
            )

            assert page.status == "error"
            assert page.error_message is not None
