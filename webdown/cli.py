"""Command-line interface for webdown.

This module provides the command-line interface (CLI) for Webdown, a tool for
converting web pages to clean, readable Markdown format. The CLI allows users to
customize various aspects of the conversion process, from content selection to
formatting options.

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

## Advanced Options

Advanced formatting options for fine-tuning the Markdown output:

* `--single-line-break`: Use single line breaks instead of two line breaks
* `--unicode`: Use Unicode characters instead of ASCII equivalents
* `--tables-as-html`: Keep tables as HTML instead of converting to Markdown
* `--emphasis-mark CHAR`: Character(s) to use for emphasis (default: '_')
* `--strong-mark CHARS`: Character(s) to use for strong emphasis (default: '**')

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

4. Show download progress for large pages and customize Markdown formatting:
   ```bash
   webdown https://example.com -p --single-line-break --unicode -o output.md
   ```

5. Extract content from a specific div and customize emphasis markers:
   ```bash
   webdown https://example.com -s "#content" --emphasis-mark "*" \
     --strong-mark "__" -o output.md
   ```

The entry point is the `main()` function, which is called when the command
`webdown` is executed.
"""

import argparse
import sys
from typing import List, Optional

import requests

from webdown import __version__
from webdown.converter import WebdownConfig, WebdownError, convert_url_to_markdown


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

    # Add advanced HTML2Text options
    advanced_group = parser.add_argument_group("Advanced Options")
    advanced_group.add_argument(
        "--single-line-break",
        action="store_true",
        help="Use single line breaks instead of double (creates more compact output)",
    )
    advanced_group.add_argument(
        "--unicode",
        action="store_true",
        help="Use Unicode characters instead of ASCII equivalents",
    )
    advanced_group.add_argument(
        "--protect-links",
        action="store_true",
        help="Protect links from line wrapping (keeps URLs on a single line)",
    )
    advanced_group.add_argument(
        "--images-as-html",
        action="store_true",
        help="Keep images as HTML rather than converting to Markdown format",
    )
    advanced_group.add_argument(
        "--tables-as-html",
        action="store_true",
        help="Keep tables as HTML instead of converting to Markdown",
    )
    advanced_group.add_argument(
        "--emphasis-mark",
        default="_",
        metavar="CHAR",
        help="Character(s) for emphasis (default: '_', alternative: '*')",
    )
    advanced_group.add_argument(
        "--strong-mark",
        default="**",
        metavar="CHARS",
        help="Character(s) for strong emphasis (default: '**', alt: '__')",
    )
    advanced_group.add_argument(
        "--default-image-alt",
        default="",
        metavar="TEXT",
        help="Default alt text for images that don't have any (default: empty string)",
    )
    advanced_group.add_argument(
        "--pad-tables",
        action="store_true",
        help="Add padding spaces for table alignment in Markdown output",
    )
    advanced_group.add_argument(
        "--wrap-list-items",
        action="store_true",
        help="Wrap list items to the specified body width",
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
            # Basic options
            url=parsed_args.url,
            include_toc=parsed_args.toc,
            include_links=not parsed_args.no_links,
            include_images=not parsed_args.no_images,
            css_selector=parsed_args.css,
            compact_output=parsed_args.compact,
            body_width=parsed_args.width,
            show_progress=parsed_args.progress,
            # Advanced options
            single_line_break=parsed_args.single_line_break,
            protect_links=parsed_args.protect_links,
            images_as_html=parsed_args.images_as_html,
            unicode_snob=parsed_args.unicode,
            tables_as_html=parsed_args.tables_as_html,
            emphasis_mark=parsed_args.emphasis_mark,
            strong_mark=parsed_args.strong_mark,
            default_image_alt=parsed_args.default_image_alt,
            pad_tables=parsed_args.pad_tables,
            wrap_list_items=parsed_args.wrap_list_items,
        )

        # Convert using the config object
        markdown = convert_url_to_markdown(config)

        if parsed_args.output:
            with open(parsed_args.output, "w", encoding="utf-8") as f:
                f.write(markdown)
        else:
            sys.stdout.write(markdown)

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
