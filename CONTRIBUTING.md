# Contributing to Webdown

Thank you for your interest in contributing to Webdown! This document provides guidelines and instructions for contributing to this project.

## Development Environment Setup

### Prerequisites

- Python 3.10 or higher
- [Poetry](https://python-poetry.org/docs/#installation) for dependency management
- Git

### Setting Up Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/kelp/webdown.git
   cd webdown
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Install pre-commit hooks:
   ```bash
   poetry run pre-commit install
   ```

### Development Commands

We use a Makefile to simplify common development tasks:

- Install dependencies: `make install`
- Install for local development: `make install-dev`
- Run tests: `make test`
- Run tests with coverage: `make test-coverage`
- Run integration tests: `make integration-test`
- Run linting: `make lint`
- Run type checking: `make type-check`
- Format code: `make format`
- Run all checks: `make all-checks`

You can also use Poetry directly:
```bash
poetry run pytest
poetry run mypy webdown
poetry run flake8 webdown
poetry run black webdown
```

## Coding Standards

### Code Style

This project follows PEP 8 conventions with some modifications enforced by Black and flake8:

- Use 4 spaces for indentation (enforced by Black)
- Line length is limited to 88 characters (enforced by Black)
- Follow naming conventions:
  - Classes: `CamelCase`
  - Functions and variables: `snake_case`
  - Constants: `UPPER_CASE`

### Type Hinting

All code should use Python type hints:

```python
def function(parameter: str, optional_param: Optional[int] = None) -> bool:
    """Function documentation."""
    ...
```

### Documentation

- All modules, classes, and functions should have docstrings.
- Use the Google docstring format:

```python
def function(param1: str, param2: int) -> bool:
    """Short description of function.

    Longer description explaining details if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ExceptionType: When and why this exception is raised
    """
```

### Updating Documentation

After making changes to the codebase, especially when adding new features or modifying existing ones:

1. Update the docstrings in the code with implementation details
2. Update the README.md with any new command-line options or examples
3. Update CHANGELOG.md with user-facing changes

The CLI argument parser in `webdown/cli.py` is the source of truth for command-line options, and the README.md is the main user documentation.

### Error Handling

- Use custom exception classes defined in `converter.py`
- Provide meaningful error messages
- Document all possible exceptions in docstrings

## Testing

### Writing Tests

- Write tests for all new functionality
- Tests should be placed in the `webdown/tests` directory
- Follow test class naming: `TestClassName`
- Follow test method naming: `test_functionality_being_tested`
- Use fixtures where appropriate to reduce code duplication

### Running Tests

- Run all tests: `make test`
- Run with coverage: `make test-coverage`
- Run integration tests: `make integration-test`

## Pull Request Process

1. Fork the repository and create a feature branch
2. Implement your changes, following the coding standards
3. Ensure all tests pass, including new tests for your feature
4. Update documentation if needed
5. Submit a pull request with a clear description of the changes
6. Address any feedback in code reviews

## Versioning

We follow [Semantic Versioning](https://semver.org/):

- MAJOR version for incompatible API changes
- MINOR version for functionality added in a backward-compatible manner
- PATCH version for backward-compatible bug fixes

## Publishing to PyPI (Maintainers Only)

Webdown uses GitHub Actions to automate the release process:

1. Update version numbers in all files at once using the bump-version command:
   ```bash
   make bump-version VERSION=0.6.0
   ```
   This will automatically update:
   - `pyproject.toml`
   - `webdown/__init__.py`

2. Update `CHANGELOG.md` with the new version and changes (this must be done manually)

3. Commit the version bump changes:
   ```bash
   git add pyproject.toml webdown/__init__.py CHANGELOG.md
   git commit -m "Bump version to 0.6.0"
   ```

4. Run the release target to verify everything and create the tag:
   ```bash
   make release
   ```
   If you're sure everything is correct and want to create the tag in one step:
   ```bash
   make release CONFIRM=yes
   ```

5. If the release target succeeds, push the tag to trigger the release workflow:
   ```bash
   git push origin v0.6.0
   ```

6. The GitHub Actions workflow will automatically:
   - Verify the version numbers match
   - Run tests
   - Build the package
   - Create a GitHub release with content from CHANGELOG.md
   - Publish to PyPI automatically

For local testing before a release, you can use:
- `make build` to build the package locally
- `make publish-test` to publish to TestPyPI

### Troubleshooting Release Issues

If the release workflow fails due to version mismatch:
1. Check that versions match in `pyproject.toml` and `webdown/__init__.py`
2. If they don't match, use `make bump-version VERSION=x.y.z` to fix the discrepancy
3. Commit the changes and try the release process again

Note: PyPI publishing uses GitHub's OIDC and PyPI's Trusted Publishers feature for secure authentication without tokens.

## License

By contributing to this project, you agree that your contributions will be licensed under the project's MIT License (see LICENSE file).

## Questions?

If you have any questions or need help, please open an issue or contact the maintainers directly.

Thank you for your contributions!
