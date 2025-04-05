# CLI Cheat Sheet

Quick reference guide for the Webdown command-line interface.

## Basic Commands

```bash
# Basic URL conversion
webdown -u https://example.com

# Basic file conversion
webdown -f ./page.html

# Save to file (URL)
webdown -u https://example.com -o output.md

# Save to file (local HTML)
webdown -f ./page.html -o output.md

# Generate table of contents
webdown -u https://example.com -t

# Show progress bar
webdown -u https://example.com -p

# Extract specific content
webdown -u https://example.com -s "main"

# Plain text version (no links/images)
webdown -u https://example.com -L -I

# Compact output with width of 80 chars
webdown -u https://example.com -c -w 80
```

## Advanced Usage

```bash
# Single line breaks (more compact)
webdown -u https://example.com --single-line-break

# Unicode support
webdown -u https://example.com --unicode

# Custom emphasis markers
webdown -u https://example.com --emphasis-mark "*" --strong-mark "__"

# Keep tables as HTML
webdown -u https://example.com --tables-as-html

# Streaming mode for large documents (5MB threshold)
webdown -u https://example.com --stream-threshold 5242880

# Protect links from wrapping
webdown -u https://example.com --protect-links

# Images as HTML
webdown -u https://example.com --images-as-html

# Default alt text for images
webdown -u https://example.com --default-image-alt "image"

# Add padding to tables
webdown -u https://example.com --pad-tables

# Wrap list items
webdown -u https://example.com --wrap-list-items
```

## Complete Example

```bash
# Extract main content, add TOC, compact output, 80 char width,
# show progress, use Unicode, and single line breaks
webdown -u https://example.com -s "main" -t -c -w 80 -p \
  --unicode --single-line-break -o output.md
```

## Options Reference

| Category | Option | Description |
|----------|--------|-------------|
| **Output** | `-o FILE` | Write to file |
| | `-p` | Show progress bar |
| **Content** | `-s SELECTOR` | CSS selector for content |
| | `-L` | Remove links |
| | `-I` | Remove images |
| **Format** | `-t` | Add table of contents |
| | `-c` | Compact output |
| | `-w N` | Set line width |
| | `--stream-threshold N` | Size threshold for streaming |
| **Advanced** | `--single-line-break` | Use single line breaks |
| | `--unicode` | Use Unicode characters |
| | `--protect-links` | Prevent link wrapping |
| | `--images-as-html` | Keep images as HTML |
| | `--tables-as-html` | Keep tables as HTML |
| | `--emphasis-mark CHAR` | Custom emphasis marker |
| | `--strong-mark CHARS` | Custom strong emphasis marker |
| | `--default-image-alt TEXT` | Default alt text |
| | `--pad-tables` | Add padding for tables |
| | `--wrap-list-items` | Wrap list items |
| **Meta** | `-V` | Show version |
| | `-h` | Show help |
