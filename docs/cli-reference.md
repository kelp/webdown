# CLI Reference

Webdown offers a straightforward command-line interface for converting web
pages to Markdown or Claude XML format.

## Basic Usage

### Single Page Conversion

```bash
webdown -u URL [options]
webdown -f FILE [options]
```

Convert a single web page or local HTML file to Markdown.

### Multi-Page Crawling

```bash
webdown crawl URL [options]
```

Crawl multiple pages from a website and convert them all.

## Complete Options Reference

### Input/Output Options

| Option | Description |
|--------|-------------|
| `-o FILE, --output FILE` | Write Markdown output to FILE instead of stdout |
| `-p, --progress` | Display a progress bar during download (useful for large pages) |

### Content Selection

| Option | Description |
|--------|-------------|
| `-s SELECTOR, --css SELECTOR` | Extract content matching CSS selector (e.g., 'main', '.content') |
| `-L, --no-links` | Convert hyperlinks to plain text (remove all link markup) |
| `-I, --no-images` | Exclude images from the output completely |

### Formatting Options

| Option | Description |
|--------|-------------|
| `-t, --toc` | Generate a table of contents based on headings in the document |
| `-c, --compact` | Remove excessive blank lines for more compact output |
| `-w N, --width N` | Set line width (0 disables wrapping, 80 recommended for readability) |

### Claude XML Options

| Option | Description |
|--------|-------------|
| `--claude-xml` | Output in Claude XML format instead of Markdown |
| `--metadata` | Include metadata section in XML (default) |
| `--no-metadata` | Exclude metadata section from XML |

### Meta Options

| Option | Description |
|--------|-------------|
| `-V, --version` | Show version information and exit |
| `-h, --help` | Show help message and exit |

## Examples with Explanations

### Basic Conversion

```bash
webdown https://example.com
```
Converts the web page at example.com to Markdown and outputs to the terminal.

### Save to File

```bash
webdown https://example.com -o example.md
```
Converts the web page and saves the output to example.md.

### Generate Table of Contents

```bash
webdown https://example.com -t
```
Adds a table of contents based on the headings found in the document.

### Extract Main Content

```bash
webdown https://example.com -s "main"
```
Extracts only the content inside the `<main>` tag, ignoring headers, footers, sidebars, etc.

### Plain Text (No Links or Images)

```bash
webdown https://example.com -L -I
```
Creates a plain text version by removing hyperlinks and images.

### Compact Output with Custom Width

```bash
webdown https://example.com -c -w 80
```
Removes excessive blank lines and wraps text at 80 characters.

### Show Progress for Large Pages

```bash
webdown https://example.com -p
```
Displays a progress bar during download, useful for large pages.

### Claude XML Format

```bash
webdown https://example.com --claude-xml -o output.xml
```
Outputs the page content in Claude XML format, optimized for use with Anthropic's Claude AI.

### Complete Example with Multiple Options

```bash
webdown https://example.com -s "main" -t -c -w 80 -p -o example.md
```
This example:
- Extracts content from the `<main>` tag
- Generates a table of contents
- Removes excessive blank lines
- Wraps text at 80 characters
- Shows a progress bar during download
- Saves output to example.md

## CLI Cheat Sheet

| Task | Command |
|------|---------|
| Basic conversion | `webdown -u https://example.com` |
| Save to file | `webdown -u https://example.com -o file.md` |
| Add table of contents | `webdown -u https://example.com -t` |
| Extract main content | `webdown -u https://example.com -s "main"` |
| Plain text version | `webdown -u https://example.com -L -I` |
| Compact output | `webdown -u https://example.com -c` |
| Set text width | `webdown -u https://example.com -w 80` |
| Show progress | `webdown -u https://example.com -p` |
| Claude XML format | `webdown -u https://example.com --claude-xml` |
| Crawl site | `webdown crawl https://docs.example.com/ -o ./output/` |
| Crawl from sitemap | `webdown crawl --sitemap https://example.com/sitemap.xml -o ./output/` |

## Crawl Command Reference

The `crawl` subcommand converts multiple pages from a website.

### Crawl Options

| Option | Description |
|--------|-------------|
| `-o DIR, --output DIR` | Output directory for converted files (required) |
| `--sitemap URL` | Parse sitemap.xml instead of crawling links |
| `--max-depth N` | Maximum crawl depth from seed URLs (default: 3) |
| `--delay SECONDS` | Delay between requests in seconds (default: 1.0) |
| `--same-domain` | Allow crawling any path on the same domain |
| `--path-prefix PREFIX` | Only crawl URLs starting with this path prefix |
| `--max-pages N` | Maximum number of pages to crawl (0 for unlimited) |
| `-q, --quiet` | Suppress progress output |

All content selection and formatting options (`-s`, `-L`, `-I`, `-t`, `-c`,
`-w`, `--claude-xml`) also work with the crawl command.

### Crawl Examples

Crawl a documentation site:

```bash
webdown crawl https://docs.example.com/ -o ./output/
```

Crawl with depth and delay settings:

```bash
webdown crawl https://docs.example.com/ -o ./output/ --max-depth 5 --delay 2.0
```

Crawl from a sitemap:

```bash
webdown crawl --sitemap https://docs.example.com/sitemap.xml -o ./output/
```

Crawl with content extraction and Claude XML output:

```bash
webdown crawl https://docs.example.com/ -o ./output/ -s "main" --claude-xml
```

Crawl only a specific path prefix:

```bash
webdown crawl https://docs.example.com/api/ -o ./output/ --path-prefix /api/
```
