"""Command-line interface for webdown.

This module provides the command-line interface (CLI) for Webdown, a tool for
converting web pages to clean, readable Markdown format. The CLI allows users to
customize various aspects of the conversion process, from content selection to
formatting options.

For a complete reference, see the [CLI Reference](../cli-reference.md) documentation.

## Basic Usage

The most basic usage is to simply provide a URL:

```bash
webdown https://example.com
```

This will fetch the web page and convert it to Markdown,
displaying the result to stdout.
To save the output to a file:

```bash
webdown https://example.com -o output.md
```

## Common Options

The CLI offers various options to customize the conversion:

* `-o, --output FILE`: Write output to FILE instead of stdout
* `-t, --toc`: Generate a table of contents based on headings
* `-L, --no-links`: Strip hyperlinks, converting them to plain text
* `-I, --no-images`: Exclude images from the output
* `-s, --css SELECTOR`: Extract only content matching the CSS selector (e.g., "main")
* `-c, --compact`: Remove excessive blank lines from the output
* `-w, --width N`: Set line width for wrapped text (0 for no wrapping)
* `-p, --progress`: Show download progress bar
* `-V, --version`: Show version information and exit
* `-h, --help`: Show help message and exit

Note: For large web pages (over 10MB), webdown automatically uses streaming mode to optimize memory usage.


## Claude XML Options

Options for generating Claude XML format, optimized for use with Claude AI:

* `--claude-xml`: Output in Claude XML format instead of Markdown
* `--metadata`: Include metadata section in XML (default: True)
* `--no-metadata`: Exclude metadata section from XML
* `--no-date`: Don't include current date in metadata

## Example Scenarios

1. Basic conversion with a table of contents:
   ```bash
   webdown https://example.com -t -o output.md
   ```

2. Extract only the main content area with compact output and text wrapping:
   ```bash
   webdown https://example.com -s "main" -c -w 80 -o output.md
   ```

3. Create a plain text version (no links or images):
   ```bash
   webdown https://example.com -L -I -o text_only.md
   ```

4. Show download progress for large pages:
   ```bash
   webdown https://example.com -p -o output.md
   ```

5. Extract content from a specific div:
   ```bash
   webdown https://example.com -s "#content" -o output.md
   ```

6. Process a large webpage with progress bar (streaming is automatic for large pages):
   ```bash
   webdown https://example.com -p
   ```

7. Generate output in Claude XML format for use with Claude AI:
   ```bash
   webdown https://example.com -s "main" --claude-xml -o output.xml
   ```

8. Create Claude XML without metadata:
   ```bash
   webdown https://example.com --claude-xml --no-metadata -o output.xml
   ```

9. Complete example with multiple options:
   ```bash
   webdown https://example.com -s "main" -t -c -w 80 -p -o output.md
   ```

The entry point is the `main()` function, which is called when the command
`webdown` is executed.
"""

import argparse
import sys
from typing import List, Optional

import requests

from webdown import __version__
from webdown.converter import (
    ClaudeXMLConfig,
    WebdownConfig,
    WebdownError,
    convert_url_to_claude_xml,
    convert_url_to_markdown,
)


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments.

    Args:
        args: Command line arguments (defaults to sys.argv[1:] if None)

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Convert web pages to clean, readable Markdown format.",
        epilog="For more information: https://github.com/kelp/webdown",
    )

    # Required argument
    parser.add_argument(
        "url",
        help="URL of the web page to convert (e.g., https://example.com)",
        nargs="?",
    )

    # Input/Output options
    io_group = parser.add_argument_group("Input/Output Options")
    io_group.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        help="Write Markdown output to FILE instead of stdout",
    )
    io_group.add_argument(
        "-p",
        "--progress",
        action="store_true",
        help="Display a progress bar during download (useful for large pages)",
    )

    # Content options
    content_group = parser.add_argument_group("Content Selection")
    content_group.add_argument(
        "-s",
        "--css",
        metavar="SELECTOR",
        help="Extract content matching CSS selector (e.g., 'main', '.content')",
    )
    content_group.add_argument(
        "-L",
        "--no-links",
        action="store_true",
        help="Convert hyperlinks to plain text (remove all link markup)",
    )
    content_group.add_argument(
        "-I",
        "--no-images",
        action="store_true",
        help="Exclude images from the output completely",
    )

    # Formatting options
    format_group = parser.add_argument_group("Formatting Options")
    format_group.add_argument(
        "-t",
        "--toc",
        action="store_true",
        help="Generate a table of contents based on headings in the document",
    )
    format_group.add_argument(
        "-c",
        "--compact",
        action="store_true",
        help="Remove excessive blank lines for more compact output",
    )
    format_group.add_argument(
        "-w",
        "--width",
        type=int,
        default=0,
        metavar="N",
        help="Set line width (0 disables wrapping, 80 recommended for readability)",
    )

    # Output Format Options
    format_group = parser.add_argument_group("Output Format Options")
    format_group.add_argument(
        "--claude-xml",
        action="store_true",
        help="Output in Claude XML format optimized for Claude AI models",
    )
    format_group.add_argument(
        "--metadata",
        action="store_true",
        default=True,
        help="Include metadata in Claude XML output (default: True)",
    )
    format_group.add_argument(
        "--no-metadata",
        action="store_false",
        dest="metadata",
        help="Exclude metadata from Claude XML output",
    )
    format_group.add_argument(
        "--no-date",
        action="store_false",
        dest="add_date",
        default=True,
        help="Don't include current date in Claude XML metadata",
    )

    # Meta options
    meta_group = parser.add_argument_group("Meta Options")
    meta_group.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show version information and exit",
    )

    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """Execute the webdown command-line interface.

    This function is the main entry point for the webdown command-line tool.
    It handles the entire workflow:
    1. Parsing command-line arguments
    2. Converting the URL to Markdown with the specified options
    3. Writing the output to a file or stdout
    4. Error handling and reporting

    Args:
        args: Command line arguments as a list of strings. If None, defaults to
              sys.argv[1:] (the command-line arguments passed to the script).

    Returns:
        Exit code: 0 for success, 1 for errors

    Examples:
        >>> main(['https://example.com'])  # Convert and print to stdout
        0
        >>> main(['https://example.com', '-o', 'output.md'])  # Write to file
        0
        >>> main(['invalid-url'])  # Handle error
        1
    """
    try:
        parsed_args = parse_args(args)

        # If no URL provided, show help
        if parsed_args.url is None:
            # This will print help and exit
            parse_args(
                ["-h"]
            )  # pragma: no cover - this exits so coverage tools can't track it
            return 0  # pragma: no cover - unreachable after SystemExit

        # Create a config object from command-line arguments
        config = WebdownConfig(
            url=parsed_args.url,
            include_toc=parsed_args.toc,
            include_links=not parsed_args.no_links,
            include_images=not parsed_args.no_images,
            css_selector=parsed_args.css,
            compact_output=parsed_args.compact,
            body_width=parsed_args.width,
            show_progress=parsed_args.progress,
        )

        # Determine output format and convert
        if parsed_args.claude_xml:
            # Create Claude XML config from CLI arguments
            claude_config = ClaudeXMLConfig(
                include_metadata=parsed_args.metadata,
                add_date=parsed_args.add_date,
            )

            # Convert to Claude XML format
            output = convert_url_to_claude_xml(config, claude_config)
        else:
            # Use standard markdown conversion
            output = convert_url_to_markdown(config)

        # Write output to file or stdout
        if parsed_args.output:
            with open(parsed_args.output, "w", encoding="utf-8") as f:
                f.write(output)
        else:
            sys.stdout.write(output)

        return 0

    except WebdownError as e:
        sys.stderr.write(f"Web conversion error: {str(e)}\n")
        return 1
    except requests.exceptions.RequestException as e:
        sys.stderr.write(f"Network error: {str(e)}\n")
        return 1
    except IOError as e:
        sys.stderr.write(f"File I/O error: {str(e)}\n")
        return 1
    except ValueError as e:
        sys.stderr.write(f"Value error: {str(e)}\n")
        return 1
    except Exception as e:
        sys.stderr.write(f"Unexpected error: {str(e)}\n")
        return 1


if __name__ == "__main__":  # pragma: no cover - difficult to test main module block
    sys.exit(main())
