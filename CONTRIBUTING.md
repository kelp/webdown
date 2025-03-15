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

## License

By contributing to this project, you agree that your contributions will be licensed under the project's MIT License (see LICENSE file).

## Questions?

If you have any questions or need help, please open an issue or contact the maintainers directly.

Thank you for your contributions!
