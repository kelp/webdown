# CLI Reference

Webdown offers a straightforward command-line interface for converting web pages to Markdown or Claude XML format.

## Basic Usage

```bash
webdown -u URL [options]
```

or

```bash
webdown -f FILE [options]
```

Where `-u URL` is the web page you want to convert (e.g., `-u https://example.com`) or `-f FILE` is the local HTML file you want to convert (e.g., `-f ./page.html`).

## Complete Options Reference

### Source Options

| Option | Description |
|--------|-------------|
| `-u URL, --url URL` | URL of the web page to convert |
| `-f FILE, --file FILE` | Path to local HTML file to convert |

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
webdown -u https://example.com
```
Converts the web page at example.com to Markdown and outputs to the terminal.

### Save to File

```bash
webdown -u https://example.com -o example.md
```
Converts the web page and saves the output to example.md.

### Generate Table of Contents

```bash
webdown -u https://example.com -t
```
Adds a table of contents based on the headings found in the document.

### Extract Main Content

```bash
webdown -u https://example.com -s "main"
```
Extracts only the content inside the `<main>` tag, ignoring headers, footers, sidebars, etc.

### Plain Text (No Links or Images)

```bash
webdown -u https://example.com -L -I
```
Creates a plain text version by removing hyperlinks and images.

### Compact Output with Custom Width

```bash
webdown -u https://example.com -c -w 80
```
Removes excessive blank lines and wraps text at 80 characters.

### Show Progress for Large Pages

```bash
webdown -u https://example.com -p
```
Displays a progress bar during download, useful for large pages.

### Claude XML Format

```bash
webdown -u https://example.com --claude-xml -o output.xml
```
Outputs the page content in Claude XML format, optimized for use with Anthropic's Claude AI.

### Complete Example with Multiple Options

```bash
webdown -u https://example.com -s "main" -t -c -w 80 -p -o example.md
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
| Basic URL conversion | `webdown -u https://example.com` |
| Basic file conversion | `webdown -f ./page.html` |
| Save to file | `webdown -u https://example.com -o file.md` |
| Add table of contents | `webdown -u https://example.com -t` |
| Extract main content | `webdown -u https://example.com -s "main"` |
| Plain text version | `webdown -u https://example.com -L -I` |
| Compact output | `webdown -u https://example.com -c` |
| Set text width | `webdown -u https://example.com -w 80` |
| Show progress | `webdown -u https://example.com -p` |
| Claude XML format | `webdown -u https://example.com --claude-xml` |
