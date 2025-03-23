# Table of Contents Generation in Webdown

Webdown provides powerful Table of Contents (TOC) generation capabilities for web pages you convert to Markdown or Claude XML format.

## Basic Usage

To generate a TOC, use the `--toc` flag:

```bash
webdown --toc https://example.com
```

This will:
1. Extract all headings (h1-h6) from the page
2. Create a nested TOC based on the heading levels
3. Add the TOC at the beginning of the output
4. Create anchor links to each heading

## Customizing TOC Generation

### Controlling TOC Depth

By default, Webdown includes all heading levels (h1-h6) in the TOC. You can limit the depth with `--toc-depth`:

```bash
webdown --toc --toc-depth 3 https://example.com
```

This includes only h1, h2, and h3 headings in the TOC.

### TOC Title

By default, the TOC is titled "Table of Contents". You can customize this with `--toc-title`:

```bash
webdown --toc --toc-title "Content Summary" https://example.com
```

### Placement

The TOC is always placed at the beginning of the document, after any metadata but before the main content.

## How TOC Links Work

### Link Generation

For each heading in the document, Webdown:

1. Extracts the heading text
2. Removes HTML tags (if any remain)
3. Converts the text to lowercase
4. Replaces spaces with hyphens
5. Removes special characters that would break Markdown links
6. Creates a unique ID if duplicate headings exist (by appending -1, -2, etc.)

For example:
- Heading "Getting Started" becomes `#getting-started`
- Heading "Section 2.1: Examples" becomes `#section-21-examples`

### Duplicate Heading Handling

Webdown automatically detects duplicate heading text and adds numeric suffixes to ensure each link is unique:

```markdown
## Installation
... content ...

## Installation
... content ...
```

The TOC will generate:
```markdown
- [Installation](#installation)
- [Installation](#installation-1)
```

## Integration with Claude XML

When using `--claude-xml` with `--toc`, Webdown:

1. Generates the TOC with proper Markdown formatting
2. Places it at the beginning of the document
3. Properly escapes all content within the XML tags

Example:
```bash
webdown --claude-xml --toc https://example.com
```

Output:
```xml
<answer>
# Table of Contents

- [Introduction](#introduction)
  - [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
- [Main Content](#main-content)
  - [Section 1](#section-1)
  - [Section 2](#section-2)

# Introduction

## Getting Started

...content continues...
</answer>
```

## Technical Details

### Heading Detection

Webdown extracts headings from the HTML document using a combination of:
- Standard h1-h6 tags
- Elements with heading roles
- Elements with heading-like styling

This ensures comprehensive heading detection across different website structures.

### Limitations

- Links to headings in code blocks might not work (code blocks often contain # characters that aren't headings)
- Very complex heading texts with unusual characters might have simplified link targets
- Some Markdown viewers might have slight differences in how they generate heading IDs

## Best Practices

For optimal TOC results:

1. Consider using CSS selectors to extract only the main content:
   ```bash
   webdown --toc --css "main, article, .content" https://example.com
   ```

2. For very large documents, limit the TOC depth:
   ```bash
   webdown --toc --toc-depth 2 https://example.com
   ```

3. When creating content for Claude, combine with other relevant options:
   ```bash
   webdown --claude-xml --toc --compact --body-width 80 https://example.com
   ```
