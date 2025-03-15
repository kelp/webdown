# Webdown Project TODO

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
- [x] Generate API documentation with pydoc
  - [x] Create docs/api/ directory with HTML documentation
  - [x] Create custom index.html as documentation entry point
- [x] Expand README.md with more detailed usage examples
- [x] Add contributing guidelines
  - [x] Create CONTRIBUTING.md with development instructions
  - [x] Include coding standards and PR process
- [x] Confirm license (MIT) and update copyright information
- [x] Improve API documentation
  - [x] Auto-generate API docs with pydoc
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
- [ ] Publish to PyPI with Poetry
  - [ ] Create PyPI account and configure credentials
  - [ ] Verify all package metadata is correct
  - [ ] Run `poetry publish --build` command
  - [ ] Update documentation with installation instructions from PyPI

## Features to Consider
- [x] Add a progress bar for downloads
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
- [ ] Interactive mode to select page sections to convert
- [x] Option to compact output by removing excessive blank lines
- [x] Remove zero-width spaces and other invisible characters
- [ ] Post-processing option to clean and normalize generated Markdown
- [x] Add command-line option to set html2text body_width (currently hard-coded to 0)
