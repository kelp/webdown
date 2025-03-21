# CLI Reference

Webdown provides a powerful command-line interface for converting web pages to Markdown. This page provides a comprehensive reference for all available options.

## Basic Usage

```bash
webdown URL [options]
```

Where `URL` is the web page you want to convert (e.g., `https://example.com`).

## Option Groups

The options are organized into several groups:

- **Input/Output Options**: Control where output is written and download progress display
- **Content Selection**: Choose which parts of the page to include or exclude
- **Formatting Options**: Customize the Markdown output format
- **Advanced Options**: Fine-tune the HTML to Markdown conversion process
- **Meta Options**: Show version information and help

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
| `--stream-threshold BYTES` | Size threshold in bytes for using streaming mode (default: 10MB, 0 to always stream) |

### Advanced Options

| Option | Description |
|--------|-------------|
| `--single-line-break` | Use single line breaks instead of double (creates more compact output) |
| `--unicode` | Use Unicode characters instead of ASCII equivalents |
| `--protect-links` | Protect links from line wrapping (keeps URLs on a single line) |
| `--images-as-html` | Keep images as HTML rather than converting to Markdown format |
| `--tables-as-html` | Keep tables as HTML instead of converting to Markdown |
| `--emphasis-mark CHAR` | Character(s) for emphasis (default: '_', alternative: '*') |
| `--strong-mark CHARS` | Character(s) for strong emphasis (default: '**', alt: '__') |
| `--default-image-alt TEXT` | Default alt text for images that don't have any (default: empty string) |
| `--pad-tables` | Add padding spaces for table alignment in Markdown output |
| `--wrap-list-items` | Wrap list items to the specified body width |

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

### Using Single Line Breaks

```bash
webdown https://example.com --single-line-break
```
Uses single line breaks instead of double line breaks, creating more compact output.

### Unicode Support

```bash
webdown https://example.com --unicode
```
Preserves Unicode characters instead of converting them to ASCII equivalents.

### Custom Emphasis Markers

```bash
webdown https://example.com --emphasis-mark "*" --strong-mark "__"
```
Uses asterisks for emphasis (*text*) and double underscores for strong emphasis (__text__).

### HTML Tables

```bash
webdown https://example.com --tables-as-html
```
Keeps tables as HTML instead of converting them to Markdown format.

### Streaming Large Documents

```bash
webdown https://example.com --stream-threshold 5242880
```
Uses streaming mode for documents larger than 5MB to optimize memory usage.

### Protect Links from Wrapping

```bash
webdown https://example.com --protect-links
```
Prevents links from being wrapped, keeping URLs on a single line.

### Complete Example with Multiple Options

```bash
webdown https://example.com -s "main" -t -c -w 80 --unicode --single-line-break -p -o example.md
```
This example:
- Extracts content from the `<main>` tag
- Generates a table of contents
- Removes excessive blank lines
- Wraps text at 80 characters
- Preserves Unicode characters
- Uses single line breaks
- Shows a progress bar during download
- Saves output to example.md

## CLI Cheat Sheet

| Task | Command |
|------|---------|
| Basic conversion | `webdown https://example.com` |
| Save to file | `webdown https://example.com -o file.md` |
| Add table of contents | `webdown https://example.com -t` |
| Extract main content | `webdown https://example.com -s "main"` |
| Plain text version | `webdown https://example.com -L -I` |
| Compact output | `webdown https://example.com -c` |
| Set text width | `webdown https://example.com -w 80` |
| Show progress | `webdown https://example.com -p` |
| Single line breaks | `webdown https://example.com --single-line-break` |
| Unicode support | `webdown https://example.com --unicode` |
| Customize emphasis | `webdown https://example.com --emphasis-mark "*"` |
| Protect links | `webdown https://example.com --protect-links` |
| Images as HTML | `webdown https://example.com --images-as-html` |
| Tables as HTML | `webdown https://example.com --tables-as-html` |
| Default image alt text | `webdown https://example.com --default-image-alt "image"` |
| Pad tables | `webdown https://example.com --pad-tables` |
| Wrap list items | `webdown https://example.com --wrap-list-items` |
| Optimize for large docs | `webdown https://example.com --stream-threshold 1048576` |
