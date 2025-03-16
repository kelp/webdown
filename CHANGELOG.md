# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
