"""Tests for the output_manager module."""

import json
import os
import tempfile
from datetime import datetime

from webdown.config import OutputFormat
from webdown.output_manager import (
    CrawledPage,
    CrawlResult,
    _sanitize_path,
    ensure_output_directory,
    get_relative_path,
    url_to_filepath,
    write_manifest,
    write_output_file,
)


class TestUrlToFilepath:
    """Tests for url_to_filepath function."""

    def test_basic_url(self) -> None:
        """Test converting a basic URL to filepath."""
        path = url_to_filepath(
            "https://example.com/docs/page",
            "/output",
            OutputFormat.MARKDOWN,
        )
        assert path == "/output/example.com/docs/page.md"

    def test_url_with_trailing_slash(self) -> None:
        """Test URL ending with slash becomes index."""
        path = url_to_filepath(
            "https://example.com/docs/",
            "/output",
            OutputFormat.MARKDOWN,
        )
        assert path == "/output/example.com/docs/index.md"

    def test_root_url(self) -> None:
        """Test root URL becomes index."""
        path = url_to_filepath(
            "https://example.com/",
            "/output",
            OutputFormat.MARKDOWN,
        )
        assert path == "/output/example.com/index.md"

    def test_url_without_path(self) -> None:
        """Test URL without path becomes index."""
        path = url_to_filepath(
            "https://example.com",
            "/output",
            OutputFormat.MARKDOWN,
        )
        assert path == "/output/example.com/index.md"

    def test_html_extension_stripped(self) -> None:
        """Test .html extension is stripped."""
        path = url_to_filepath(
            "https://example.com/page.html",
            "/output",
            OutputFormat.MARKDOWN,
        )
        assert path == "/output/example.com/page.md"

    def test_htm_extension_stripped(self) -> None:
        """Test .htm extension is stripped."""
        path = url_to_filepath(
            "https://example.com/page.htm",
            "/output",
            OutputFormat.MARKDOWN,
        )
        assert path == "/output/example.com/page.md"

    def test_claude_xml_extension(self) -> None:
        """Test Claude XML format uses .xml extension."""
        path = url_to_filepath(
            "https://example.com/page",
            "/output",
            OutputFormat.CLAUDE_XML,
        )
        assert path == "/output/example.com/page.xml"

    def test_port_in_url(self) -> None:
        """Test URL with port number."""
        path = url_to_filepath(
            "https://example.com:8080/page",
            "/output",
            OutputFormat.MARKDOWN,
        )
        assert "example.com_8080" in path

    def test_deep_path(self) -> None:
        """Test URL with deep path structure."""
        path = url_to_filepath(
            "https://example.com/docs/guide/getting-started/intro",
            "/output",
            OutputFormat.MARKDOWN,
        )
        assert path == "/output/example.com/docs/guide/getting-started/intro.md"


class TestSanitizePath:
    """Tests for _sanitize_path function."""

    def test_normal_path(self) -> None:
        """Test normal path passes through."""
        assert _sanitize_path("docs/page") == "docs/page"

    def test_special_characters(self) -> None:
        """Test special characters are replaced."""
        result = _sanitize_path('docs/page<>:"|?*name')
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result

    def test_empty_path(self) -> None:
        """Test empty path returns index."""
        assert _sanitize_path("") == "index"

    def test_long_path_component(self) -> None:
        """Test long path components are truncated."""
        long_name = "a" * 250
        result = _sanitize_path(long_name)
        assert len(result) <= 200


class TestCrawlResult:
    """Tests for CrawlResult dataclass."""

    def test_successful_count(self) -> None:
        """Test counting successful pages."""
        result = CrawlResult(
            pages=[
                CrawledPage(
                    url="https://example.com/1",
                    output_path="1.md",
                    title="Page 1",
                    crawled_at=datetime.now(),
                    depth=0,
                    status="success",
                ),
                CrawledPage(
                    url="https://example.com/2",
                    output_path="2.md",
                    title="Page 2",
                    crawled_at=datetime.now(),
                    depth=0,
                    status="error",
                    error_message="Failed",
                ),
                CrawledPage(
                    url="https://example.com/3",
                    output_path="3.md",
                    title="Page 3",
                    crawled_at=datetime.now(),
                    depth=0,
                    status="success",
                ),
            ]
        )
        assert result.successful_count == 2
        assert result.error_count == 1
        assert result.skipped_count == 0

    def test_empty_result(self) -> None:
        """Test empty result has zero counts."""
        result = CrawlResult()
        assert result.successful_count == 0
        assert result.error_count == 0
        assert result.skipped_count == 0


class TestWriteManifest:
    """Tests for write_manifest function."""

    def test_write_manifest(self) -> None:
        """Test writing manifest to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = CrawlResult(
                pages=[
                    CrawledPage(
                        url="https://example.com/page",
                        output_path="example.com/page.md",
                        title="Test Page",
                        crawled_at=datetime(2025, 1, 15, 10, 30, 0),
                        depth=0,
                        status="success",
                    ),
                ],
                start_time=datetime(2025, 1, 15, 10, 0, 0),
                end_time=datetime(2025, 1, 15, 10, 30, 0),
                seed_urls=["https://example.com/"],
                max_depth=3,
                output_format="markdown",
            )

            manifest_path = write_manifest(result, tmpdir)
            assert os.path.exists(manifest_path)

            with open(manifest_path) as f:
                manifest = json.load(f)

            assert manifest["version"] == "1.0"
            assert manifest["crawl_info"]["total_pages"] == 1
            assert manifest["crawl_info"]["successful"] == 1
            assert len(manifest["pages"]) == 1
            assert manifest["pages"][0]["url"] == "https://example.com/page"


class TestWriteOutputFile:
    """Tests for write_output_file function."""

    def test_write_creates_directories(self) -> None:
        """Test that write_output_file creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "a", "b", "c", "file.md")
            write_output_file(filepath, "test content")

            assert os.path.exists(filepath)
            with open(filepath) as f:
                assert f.read() == "test content"


class TestGetRelativePath:
    """Tests for get_relative_path function."""

    def test_relative_path(self) -> None:
        """Test getting relative path."""
        rel = get_relative_path("/output/example.com/page.md", "/output")
        assert rel == "example.com/page.md"


class TestEnsureOutputDirectory:
    """Tests for ensure_output_directory function."""

    def test_creates_nested_dirs(self) -> None:
        """Test creating nested directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "a", "b", "c", "file.md")
            ensure_output_directory(filepath)
            assert os.path.isdir(os.path.dirname(filepath))
