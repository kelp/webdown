# CLI Cheat Sheet

Quick reference guide for the Webdown command-line interface.

## Basic Commands

```bash
# Basic conversion
webdown https://example.com

# Save to file
webdown https://example.com -o output.md

# Generate table of contents
webdown https://example.com -t

# Show progress bar
webdown https://example.com -p

# Extract specific content
webdown https://example.com -s "main"

# Plain text version (no links/images)
webdown https://example.com -L -I

# Compact output with width of 80 chars
webdown https://example.com -c -w 80
```

## Advanced Usage

```bash
# Single line breaks (more compact)
webdown https://example.com --single-line-break

# Unicode support
webdown https://example.com --unicode

# Custom emphasis markers
webdown https://example.com --emphasis-mark "*" --strong-mark "__"

# Keep tables as HTML
webdown https://example.com --tables-as-html

# Streaming mode for large documents (5MB threshold)
webdown https://example.com --stream-threshold 5242880

# Protect links from wrapping
webdown https://example.com --protect-links

# Images as HTML
webdown https://example.com --images-as-html

# Default alt text for images
webdown https://example.com --default-image-alt "image"

# Add padding to tables
webdown https://example.com --pad-tables

# Wrap list items
webdown https://example.com --wrap-list-items
```

## Complete Example

```bash
# Extract main content, add TOC, compact output, 80 char width,
# show progress, use Unicode, and single line breaks
webdown https://example.com -s "main" -t -c -w 80 -p \
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
