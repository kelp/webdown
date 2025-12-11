# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.0] - 2025-12-10

### Added
- **Crawler feature**: New `webdown crawl` subcommand for converting multiple
  pages from a website
- Breadth-first crawling with configurable depth and rate limiting
- Sitemap.xml parsing support with `--sitemap` option
- Scope control: `--same-domain`, `--same-subdomain`, `--path-prefix`
- Output manifest (index.json) with crawl metadata
- New Python API: `crawl()`, `crawl_from_sitemap()`, `CrawlerConfig`,
  `ScopeType`, `CrawlResult`, `CrawledPage`
- New modules: `crawler.py`, `link_extractor.py`, `output_manager.py`

### Changed
- CLI now supports subcommands (existing behavior unchanged for backward
  compatibility)
- Updated all dependencies to latest versions

### Security
- Fixed regex package vulnerability (CVE in version 2024.11.6)
- Updated cryptography 44.0.2 → 46.0.3
- Updated urllib3 2.5.0 → 2.6.1

## [0.7.1] - 2025-12-10

### Changed
- Updated all dependencies to latest versions

### Security
- Fixed regex package vulnerability (CVE in version 2024.11.6)
- Updated cryptography 44.0.2 → 46.0.3
- Updated urllib3 2.5.0 → 2.6.1

### Dependencies
- pydantic 2.9.2 → 2.12.5
- black 25.9.0 → 25.12.0
- mypy 1.18.2 → 1.19.0
- mkdocs-material 9.6.21 → 9.7.0
- coverage 7.8.0 → 7.13.0
- pre-commit 4.3.0 → 4.5.0
- beautifulsoup4 4.14.2 → 4.14.3
- regex 2024.11.6 → 2025.11.3
- actions/checkout 4 → 6
- actions/upload-artifact 4 → 5

## [0.7.0] - 2025-04-05

### Breaking Changes
- CLI interface now requires explicit `-u/--url` or `-f/--file` flags for source input
- URL must now be specified with `-u/--url` flag instead of as a positional argument
- All CLI examples in documentation have been updated to reflect the new syntax

### Added
- Support for converting local HTML files to Markdown with `-f/--file` option
- New `convert_file` function in the Python API for local HTML file conversion
- New `read_html_file` function for reading HTML from the local filesystem
- Added error codes for file-related errors (FILE_NOT_FOUND, PERMISSION_DENIED, IO_ERROR)
- Comprehensive documentation with examples for local file conversion
- Comprehensive CLI test script (`scripts/test_cli.sh`) for testing all CLI options with real websites

## [0.6.3] - 2025-03-22

### Changed
- Updated project status from Alpha to Beta to reflect stability and completeness
- Enhanced PyPI metadata with improved descriptions and keywords
- Added additional classifiers for better project categorization
- Added project URLs for documentation, bug tracker, source code, and changelog

## [0.6.2] - 2025-03-22

### Changed
- Added poetry.lock to version control for reproducible builds
- Updated all dependencies to their latest compatible versions
- Pin safety package to version 3.3.1
- Enhanced GitHub Actions workflows with better cache handling to avoid conflicts

### Security
- Updated safety scanner from 2.3.5 to 3.3.1 for improved vulnerability detection

## [0.6.1] - 2025-03-22

### Fixed
- Code style and formatting issues in test files
- GitHub Actions cache conflict warnings by improving cache key uniqueness
- Added Python version to GitHub Actions cache keys for better matrix build separation

## [0.6.0] - 2025-03-22

### Added
- Comprehensive documentation for troubleshooting and error handling
- Advanced Table of Contents (TOC) documentation with examples and customization guidance
- Documentation for streaming large files, explaining the 10MB threshold implementation
- Improved API documentation with correct module references after refactoring

### Changed
- Major refactoring to improve code organization and maintainability:
  - Split monolithic converter.py into logical modules (html_parser.py, markdown_converter.py, xml_converter.py)
  - Replaced complex placeholder system for code blocks with direct processing
  - Reduced XML helper functions from 7+ to 3-4 clear functions
  - Created reusable validation and error handling utilities
  - Consolidated configuration into dedicated classes (WebdownConfig, DocumentOptions)
  - Eliminated duplicate code in XML converter with new `_process_paragraphs()` helper function
- Improved test coverage to 100% across all application code
- Simplified streaming implementation with fixed 10MB threshold
- Updated configuration class documentation to reflect actual implementation
- Reorganized codebase following clean architecture principles

### Fixed
- Documentation build after modular architecture refactoring
- Corrected API references in documentation
- Validation issues in error handling code
- Improved error reporting for various failure scenarios

## [0.5.0] - 2025-03-21

### Added
- Claude XML format support with `--claude-xml` flag
- Optimized XML structure for use with Anthropic's Claude AI models
- Metadata handling in Claude XML output with `--no-metadata` and `--no-date` options
- New test suite for Claude XML functionality
- Documentation for Claude XML format

### Changed
- Simplified streaming implementation with fixed 10MB threshold
- Removed `stream_threshold` parameter from WebdownConfig
- Removed advanced HTML2Text options to simplify the API
- Improved README documentation for clarity and simplicity
- Added code quality improvement tasks to TODO.md

### Fixed
- Improved streaming mode detection reliability
- Better error handling in the streaming implementation

## [0.4.2] - 2025-03-16

### Improved
- Migrated documentation to MkDocs with Material theme for better API reference
- Added proper documentation site with auto-generation from docstrings
- Fixed documentation deployment to GitHub Pages
- Improved docstrings to be more consistent across modules

## [0.4.1] - 2025-03-15

### Added
- Added pdoc documentation generation with `make docs` and `make docs-serve` commands
- Generated documentation now available in the `docs/` directory

### Improved
- Enhanced CLI documentation with detailed explanations and practical examples
- Improved command-line help with logically organized option groups and better descriptions
- Added epilog with link to project repository

## [0.4.0] - 2025-03-15

### Added
- Introduced WebdownConfig class for better parameter organization and configuration
- Added comprehensive support for advanced HTML2Text options in both CLI and API:
  - Single line break mode (`--single-line-break`)
  - Unicode character support (`--unicode`)
  - HTML tables preservation (`--tables-as-html`)
  - Custom emphasis and strong emphasis markers (`--emphasis-mark`, `--strong-mark`)
  - Link protection, image handling options, and more in the API
- Improved CLI with advanced options group for better help display

### Changed
- Simplified the exception hierarchy to a single WebdownError class
- Updated API to support both parameter-based and config-based approaches
- Improved documentation with detailed examples for new features
- Updated all dependencies to latest versions
- html2text updated from 2020.1.16 to 2024.2.26
- beautifulsoup4, requests, tqdm and all dev dependencies updated to latest versions

## [0.3.1] - 2025-03-15

### Changed
- Updated all dependencies to latest versions
- html2text updated from 2020.1.16 to 2024.2.26
- beautifulsoup4, requests, tqdm and all dev dependencies updated to latest versions

## [0.3.0] - 2025-03-15

### Added
- Command-line option `-w/--width` to set html2text body_width for text wrapping
- Progress bar for downloads with new `-p/--progress` flag
- Support for CSS selectors with `-s/--css` to extract specific page sections
- Compact output option with `-c/--compact` to remove excessive blank lines
- Automatic removal of zero-width spaces and other invisible characters

### Changed
- Migrated to modern Python packaging using Poetry
- Updated Python requirements to 3.10+
- Changed CSS selector flag from `-c` to `-s` to avoid conflict with compact flag
- Improved documentation with comprehensive docstrings
- Enhanced test coverage to 100% (excluding integration tests)

## [0.2.0] - 2025-03-12

### Added
- Initial release with basic web to markdown conversion
- Support for table of contents generation
- Link and image handling options
