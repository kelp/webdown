# Claude XML Format Support

Webdown includes support for generating Claude XML, a structured format optimized for use with Anthropic's Claude AI models. This format helps Claude better understand and process the content.

## Benefits of Claude XML

- **Better content organization**: Helps Claude understand the structure of your content
- **Improved code handling**: Code blocks are properly tagged with language information
- **Metadata support**: Includes title, source URL, and date information

## Using Claude XML Format

To generate Claude XML output, use the `--claude-xml` flag:

```bash
webdown https://example.com --claude-xml -o output.xml
```

### Available Options

- `--claude-xml`: Output in Claude XML format instead of Markdown
- `--metadata`: Include metadata section in XML (default: True)
- `--no-metadata`: Exclude metadata section from XML

## XML Structure

The Claude XML format used by webdown follows this structure:

```xml
<claude_documentation>
  <metadata>
    <title>Documentation Title</title>
    <source>https://source-url.com</source>
    <date>2025-03-20</date>
  </metadata>

  <content>
    <section>
      <heading>Section Heading</heading>
      <text>Regular paragraph text goes here...</text>

      <code language="python">
def example_function():
    return "This is a code example"
      </code>
    </section>
  </content>
</claude_documentation>
```

## Example Usage

```bash
# Basic Claude XML conversion
webdown https://example.com --claude-xml -o output.xml

# Extract specific content with no metadata
webdown https://example.com -s "main" --claude-xml --no-metadata -o api_docs.xml

# Compact output with no images
webdown https://example.com -I -c --claude-xml -o content.xml
```

## Python API Usage

```python
from webdown.converter import convert_url_to_claude_xml

# Basic usage
xml = convert_url_to_claude_xml("https://example.com")

# Save to file
with open("output.xml", "w") as f:
    f.write(xml)
```
