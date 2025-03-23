# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
