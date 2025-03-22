# Webdown Project TODO

## Bug Fixes and Quality Issues
- [x] Fix stream decoding inconsistency in progress reporting
  - [x] Review and fix lines 153-158 in converter.py where we use `decode_unicode=True` but measure encoded chunk length
  - [x] Test with large web pages to verify progress bar accuracy
- [x] Improve error handling consistency
  - [x] Replace generic `except Exception` in cli.py with specific exception handling
  - [x] Ensure all WebdownError exceptions include meaningful contextual information
- [x] Add parameter validation
  - [x] Validate CSS selectors before use to provide better error messages
  - [x] Add validation for width parameter and other numeric inputs
- [x] Fix TOC generation issues
  - [x] Improve heading detection to handle code blocks with # characters
  - [x] Fix link generation in TOC to properly handle special characters in heading titles
  - [x] Add proper duplicate link handling with suffixes
- [x] Expose all WebdownConfig parameters in CLI
  - [x] Add missing parameters like protect_links, images_as_html, etc. to CLI interface
  - [x] Update CLI documentation to reflect new parameters
- [x] Optimize performance for large documents
  - [x] Improve progress bar implementation to avoid extra HEAD request
  - [x] Implement streaming processing for very large documents with threshold control
- [x] Add dependency security scanning
  - [x] Set up security scanning in CI/CD pipeline to check for vulnerabilities
  - [x] Create plan for addressing detected vulnerabilities (SECURITY.md)

## Remaining Items (decided not to change)
- The mypy configuration using Python 3.13 is intentional - we want to type check against the latest Python version while still supporting older versions at runtime.

## Environment Setup
- [x] Set up proper Python development environment with pyenv
  - [x] Create `.python-version` file with appropriate Python version
  - [x] Run `pyenv install` if needed to install specified version
  - [x] Ensure that `pyenv` is properly initialized in shell profile
- [x] Move to Poetry for environment management
  - [x] Configure Poetry to use Python 3.10+
  - [x] Set up dependencies in pyproject.toml
  - [x] Replace legacy venv-based approach
- [x] Install development dependencies through Poetry

## Testing
- [x] Run all unit tests: `pytest`
- [x] Run tests with coverage: `pytest --cov=webdown`
- [x] Run integration tests: `pytest --integration`
- [x] Fix any failing tests
- [x] Ensure all code paths are properly tested (aim for 100% coverage)
  - [x] Fix coverage for CLI module with proper pragma handling
  - [x] Fix coverage for converter module

## Code Quality
- [x] Run linting: `flake8 webdown`
- [x] Run type checking: `mypy webdown`
- [x] Fix formatting issues with Black and isort
- [x] Fix type annotation issues in test files
- [x] Add modern Python project configuration:
  - [x] Create `pyproject.toml` (PEP 517/518 standard)
  - [x] Configure tools (flake8, mypy, black, isort) in pyproject.toml
  - [x] Add `.gitignore` entries for `.venv`, `__pycache__`, etc.
- [x] Consider adding pre-commit hooks for code quality
  - [x] Create `.pre-commit-config.yaml` with common Python linters
  - [x] Install with `pre-commit install`
- [x] Set up Claude commands for code quality checks

## Documentation
- [x] Verify all docstrings are complete and follow standards
  - [x] Add detailed module-level docstrings to all modules
  - [x] Add comprehensive function and class docstrings
  - [x] Include examples in docstrings where helpful
- [x] Generate API documentation with pdoc
  - [x] Add Makefile commands for generating docs (`make docs`)
  - [x] Add local documentation server command (`make docs-serve`)
  - [x] Improve formatting of docstrings with Markdown bullet lists
- [x] Expand README.md with more detailed usage examples
- [x] Add contributing guidelines
  - [x] Create CONTRIBUTING.md with development instructions
  - [x] Include coding standards and PR process
- [x] Confirm license (MIT) and update copyright information
- [x] Improve API documentation
  - [x] Better CLI documentation with improved help formatting
  - [x] Enhance WebdownConfig class documentation
  - [x] Document all functions, classes, and modules

## Local Development Best Practices
- [x] Set up local git hooks for linting/testing
- [x] Create a Makefile for common development tasks
- [x] Add format-check target to validate formatting without changing files
- [x] Ensure all targets include conftest.py and other relevant files
- [x] Document development workflow in README.md
- [x] Add local user installation target (`make install-dev`)
- [ ] Consider using tox for testing across multiple Python versions

## Packaging and Distribution
- [x] Migrate to modern Python packaging:
  - [x] Move to Poetry for dependency/package management
    - [x] Create pyproject.toml with Poetry sections
    - [x] Set up Poetry configuration
    - [x] Convert dependencies to Poetry format
  - [x] Remove legacy setup.py-based packaging files
    - [x] Remove setup.py
    - [x] Remove MANIFEST.in
    - [x] Remove egg-info directory
- [x] Pin dependency versions properly
- [x] Organize development dependencies in pyproject.toml
- [x] Update Python requirements to 3.10+ (all versions not EOL as of 2025)
- [x] Test building the package: `poetry build`
- [x] Test installing the built package
- [x] Verify the CLI script works when installed
- [x] Support local development installation with `make install-dev`

## GitHub
- [x] Update GitHub Actions workflow:
  - [x] Update to use actions/checkout@v4 and actions/setup-python@v5
  - [x] Test against modern Python versions (3.10-3.13)
  - [x] Add caching for pip dependencies
  - [x] Configure dependabot for dependency updates
- [x] Consider adding badges for:
  - [x] Tests status
  - [x] Coverage
  - [x] PyPI version
  - [x] Python versions supported
- [x] Set up branch protection rules (CODEOWNERS file added)
- [x] Create release workflow
  - [x] Set up automatic version detection
  - [x] Configure automatic PyPI publishing on new release tags
  - [x] Create GitHub release notes template from CHANGELOG.md

## Future Publishing Tasks
- [x] Publish to PyPI with Poetry
  - [x] Create PyPI account and configure credentials
  - [x] Verify all package metadata is correct
  - [x] Set up GitHub Actions for automated PyPI publishing
  - [x] Configure PyPI Trusted Publishers for secure authentication
  - [x] Update documentation with installation instructions from PyPI

## Code Improvements
- [x] Reduce dependency complexity
  - [x] Consider replacing tqdm with simple custom progress bar (~15 lines) - DECISION: Keep tqdm for better UX and cross-platform support
  - [x] Evaluate necessity of the custom exception hierarchy (WebdownError, NetworkError, etc.) - IMPLEMENTED: Simplified to single WebdownError class
  - [x] Simplify parameter interface of `convert_url_to_markdown()` (consider Config object) - IMPLEMENTED: Added WebdownConfig class while preserving backward compatibility
  - [x] Remove low-value formatting options to simplify the interface - IMPLEMENTED: Removed advanced formatting options and simplified interface
- [x] Optimize html2text usage
  - [x] Set Unicode mode to always on for better character representation
  - [x] Simplify streaming implementation with fixed 10MB threshold - IMPLEMENTED: Removed configurable threshold in favor of automatic 10MB threshold
  - [ ] Benchmark and optimize performance for large documents

## Documentation Enhancements
- [x] Complete API documentation with pdoc
  - [x] Generate HTML documentation with proper navigation
  - [x] Make CLI module part of the public API for better discoverability
  - [x] Improve docstring formatting with Markdown syntax
- [x] Improve CLI documentation
  - [x] Document all available options including the missing WebdownConfig parameters
  - [x] Provide examples for each advanced option
  - [x] Create a comprehensive CLI cheat sheet
- [ ] Add batch processing examples
  - [ ] Document how to process multiple URLs efficiently
  - [ ] Provide shell script examples for batch processing
- [ ] Include configuration recommendations
  - [ ] Add guidance for optimal settings for different site types (blogs, docs, etc.)
  - [ ] Document best practices for token efficiency with LLMs
- [ ] Improve error handling documentation
  - [ ] Explain how users should handle common failures
  - [ ] Add troubleshooting section for common issues
  - [ ] Document common error scenarios and their resolution
- [ ] Document advanced TOC functionality
  - [ ] Explain TOC link generation and limitations
  - [ ] Provide examples of customized TOC formatting
- [ ] Document automatic streaming for large files
  - [ ] Explain 10MB threshold implementation
  - [ ] Add advice for users working with very large documents
- [ ] Consider setting up ReadTheDocs or GitHub Pages for online documentation hosting

## Test Improvements
- [ ] Complete edge case coverage
  - [ ] Add tests for network failure scenarios
  - [ ] Test different HTML edge cases and encoding issues
  - [ ] Add tests for invalid CSS selectors
  - [ ] Test TOC generation with malformed headings and special characters
  - [ ] Test with very large HTML documents to verify memory usage
  - [ ] Add tests for Unicode handling and invisible character removal
  - [ ] Test automatic streaming threshold (10MB) with mocked files
- [ ] Enhance integration tests
  - [ ] Test against more diverse real-world websites
  - [ ] Add performance testing for large documents
  - [ ] Test with slow connections and timeout scenarios
  - [ ] Test progress bar accuracy with different content-length responses
  - [ ] Verify that progress bar works correctly with automatic streaming

## Features to Consider
- [x] Add a progress bar for downloads
- [x] Improve API with WebdownConfig class for better parameter organization
- [x] Support advanced HTML2Text options in both CLI and API:
  - [x] Single line break mode
  - [x] Unicode character support
  - [x] HTML tables preservation
  - [x] Custom emphasis and strong emphasis markers
- [ ] Support for custom HTML to Markdown converters
- [ ] Support for authentication for accessing private web content
- [ ] Markdown output styling options
- [ ] Batch processing of multiple URLs
- [x] Add support for extracting specific page sections via CSS selectors
  - [x] Changed `-c/--css` flag to `-s/--css` (avoid conflict with compact)
- [ ] Add caching mechanism for frequently accessed pages
- [ ] Support for generating heading IDs for better navigation
- [ ] Add option to preserve or transform HTML comments
- [ ] Support for rendering math equations (MathJax/LaTeX)
- [ ] Command-line option for output file format (Markdown, CommonMark, GitHub Flavored Markdown)

## Future Interface Simplifications
- [x] Simplify streaming with fixed 10MB threshold
  - [x] Remove stream_threshold parameter from WebdownConfig
  - [x] Update CLI parser to remove stream_threshold option
  - [x] Implement fixed 10MB threshold for automatic streaming mode
- [ ] Consider removing other low-value configuration options
  - [ ] Evaluate remaining advanced options for potential removal
  - [ ] Focus on making common use cases simple while preserving flexibility
- [ ] Improve defaults for better out-of-the-box experience
  - [ ] Set reasonable defaults for all options
  - [ ] Consider environment detection to adapt defaults to terminal capabilities

## Claude XML Format
- [x] Add Anthropic Claude XML format support
  - [x] Implement converter for Claude XML format (content wrapped in XML tags)
  - [x] Add CLI option to output in Claude XML format (`--claude-xml`)
  - [x] Include options for metadata handling in XML output
  - [x] Support for code blocks with proper language tags
  - [x] Document Claude XML format usage and examples
- [ ] Improve Claude XML format for better understanding
  - [ ] Fix code block detection and formatting in XML output
  - [ ] Enhance section hierarchy preservation (maintain h1/h2/h3 relationships)
  - [ ] Add preset CSS selectors for common documentation sites
  - [ ] Add test cases for XML format edge cases

## Additional Features
- [ ] Interactive mode to select page sections to convert
- [x] Option to compact output by removing excessive blank lines
- [x] Remove zero-width spaces and other invisible characters
- [ ] Post-processing option to clean and normalize generated Markdown
- [x] Add command-line option to set html2text body_width (currently hard-coded to 0)
- [ ] Add multi-language support for non-English websites
