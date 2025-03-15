"""Command-line interface for webdown.

This module provides the command-line interface (CLI) for webdown, allowing users
to convert web pages to Markdown from the terminal. It parses command-line arguments,
handles error reporting, and manages input/output operations.

The entry point is the `main()` function, which is called when the command
`webdown` is executed. The available options include:

  -o, --output FILE     Write output to FILE instead of stdout
  -t, --toc             Generate a table of contents based on headings
  -L, --no-links        Strip hyperlinks, converting them to plain text
  -I, --no-images       Exclude images from the output
  -s, --css SELECTOR    Extract only content matching the CSS selector
  -c, --compact         Remove excessive blank lines from the output
  -V, --version         Show version information and exit
  -h, --help            Show help message and exit

Example usage:
  webdown https://example.com -o output.md -c -t
"""

import argparse
import sys
from typing import List, Optional

from webdown import __version__
from webdown.converter import convert_url_to_markdown


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments.

    Args:
        args: Command line arguments (defaults to sys.argv[1:] if None)

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Convert web pages to markdown.")
    parser.add_argument("url", help="URL of the web page to convert", nargs="?")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    parser.add_argument(
        "-t", "--toc", action="store_true", help="Generate table of contents"
    )
    parser.add_argument(
        "-L", "--no-links", action="store_true", help="Strip hyperlinks"
    )
    parser.add_argument("-I", "--no-images", action="store_true", help="Exclude images")
    parser.add_argument("-s", "--css", help="CSS selector to extract specific content")
    parser.add_argument(
        "-c", "--compact", action="store_true", help="Remove excessive blank lines"
    )
    parser.add_argument(
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

        markdown = convert_url_to_markdown(
            parsed_args.url,
            include_toc=parsed_args.toc,
            include_links=not parsed_args.no_links,
            include_images=not parsed_args.no_images,
            css_selector=parsed_args.css,
            compact_output=parsed_args.compact,
        )

        if parsed_args.output:
            with open(parsed_args.output, "w", encoding="utf-8") as f:
                f.write(markdown)
        else:
            sys.stdout.write(markdown)

        return 0

    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        return 1


if __name__ == "__main__":  # pragma: no cover - difficult to test main module block
    sys.exit(main())
