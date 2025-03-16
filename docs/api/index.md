# API Reference

Webdown provides a simple API for converting web pages to Markdown. The main modules are:

## Modules

- [Converter](converter.md) - Core functionality for HTML to Markdown conversion
- [CLI](cli.md) - Command-line interface for the package

## Quick Start

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

For more details, see the [Converter API documentation](converter.md).
