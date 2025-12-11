# API Reference

Webdown provides a simple API for converting web pages to Markdown and crawling
entire websites. The main modules are:

## Modules

- [Converter](converter.md) - Core functionality for HTML to Markdown conversion
- [CLI](cli.md) - Command-line interface for the package

## Quick Start

### Single Page Conversion

```python
from webdown.converter import convert_url_to_markdown

# Basic usage
markdown = convert_url_to_markdown("https://example.com")

# With options
markdown = convert_url_to_markdown(
    url="https://example.com",
    include_toc=True,
    compact_output=True,
    body_width=80
)

# Save to file
with open("output.md", "w") as f:
    f.write(markdown)
```

### Multi-Page Crawling

```python
from webdown import crawl, CrawlerConfig, ScopeType

# Configure the crawler
config = CrawlerConfig(
    seed_urls=["https://docs.example.com/"],
    output_dir="./output/",
    max_depth=3,
    delay_seconds=1.0,
    scope=ScopeType.SAME_SUBDOMAIN,
)

# Crawl the site
result = crawl(config)

print(f"Crawled {result.successful_count} pages")
for page in result.pages:
    print(f"  {page.url} -> {page.output_path}")
```

### Crawl from Sitemap

```python
from webdown import crawl_from_sitemap, CrawlerConfig

config = CrawlerConfig(
    seed_urls=[],  # Not used for sitemap crawl
    output_dir="./output/",
)

result = crawl_from_sitemap(
    "https://docs.example.com/sitemap.xml",
    config
)
```

For more details, see the [Converter API documentation](converter.md).
