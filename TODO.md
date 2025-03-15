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
- [ ] Ensure all code paths are properly tested (aim for 100% coverage)

## Code Quality
- [x] Run linting: `flake8 webdown`
- [x] Run type checking: `mypy webdown`
- [x] Fix formatting issues with Black and isort
- [ ] Fix remaining type issues
- [x] Add modern Python project configuration:
  - [x] Create `pyproject.toml` (PEP 517/518 standard)
  - [x] Configure tools (flake8, mypy, black, isort) in pyproject.toml
  - [x] Add `.gitignore` entries for `.venv`, `__pycache__`, etc.
- [x] Consider adding pre-commit hooks for code quality
  - [x] Create `.pre-commit-config.yaml` with common Python linters
  - [x] Install with `pre-commit install`

## Documentation
- [ ] Verify all docstrings are complete and follow standards
- [ ] Generate API documentation with pydoc
- [x] Expand README.md with more detailed usage examples
- [ ] Add contributing guidelines

## Local Development Best Practices
- [x] Set up local git hooks for linting/testing
- [x] Create a Makefile for common development tasks:
  ```
  make lint    # Run linters
  make test    # Run tests
  make install # Install in development mode
  make clean   # Clean build artifacts
  ```
- [x] Document development workflow in README.md
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
- [ ] Test installing the built package
- [ ] Verify the CLI script works when installed

## GitHub
- [x] Update GitHub Actions workflow:
  - [x] Update to use actions/checkout@v4 and actions/setup-python@v5
  - [x] Test against modern Python versions (3.10-3.13)
  - [x] Add caching for pip dependencies
  - [x] Configure dependabot for dependency updates
- [ ] Consider adding badges for:
  - [ ] Tests status
  - [ ] Coverage
  - [ ] PyPI version
  - [ ] Python versions supported
- [ ] Set up branch protection rules

## Features to Consider
- [ ] Add a progress bar for downloads
- [ ] Support for custom HTML to Markdown converters
- [ ] Support for authentication for accessing private web content
- [ ] Markdown output styling options
- [ ] Batch processing of multiple URLs
