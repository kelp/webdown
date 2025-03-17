# Webdown Development Guide

## Working with Claude

- **No hallucinations**: If Claude is uncertain about any answer or how to do something, it should explicitly say so rather than guessing or making up information.
- **Clear uncertainty**: When encountering ambiguous requirements or unknown aspects of the codebase, Claude should openly acknowledge uncertainty and ask for clarification.
- **Providing alternatives**: When unsure about a specific solution, Claude should present multiple options along with their potential trade-offs.

## Version Management (Semantic Versioning)

We follow [Semantic Versioning](https://semver.org/) for version numbering (MAJOR.MINOR.PATCH):

- **Patch version (0.4.1 → 0.4.2)**: Documentation updates, bug fixes, and other changes that don't modify the API
- **Minor version (0.4.2 → 0.5.0)**: New features or enhancements that maintain backward compatibility
- **Major version (0.9.0 → 1.0.0)**: Breaking changes, significant rewrites, or major feature overhauls

When making changes, choose the appropriate version increment based on the impact of your changes.

## Modern Python Development Setup (Python 3.10+)

### Build & Testing Commands
- Install dependencies: `poetry install`
- Activate shell: `poetry shell`
- Run all tests: `poetry run pytest` or `make test`
- Run specific test: `poetry run pytest webdown/tests/test_file.py::TestClass::test_function`
- Run with coverage: `poetry run pytest --cov=webdown` or `make test-coverage`
- Run integration tests: `poetry run pytest --integration` or `make integration-test`
- Type checking: `poetry run mypy webdown` or `make type-check`
- Linting: `poetry run flake8 webdown` or `make lint`
- Formatting: `poetry run black webdown && poetry run isort webdown` or `make format`
- All checks: `make all-checks`
- Building package: `poetry build` or `make build`

### Development with Poetry
- Add dependency: `poetry add requests`
- Add dev dependency: `poetry add --group dev pytest`
- Update dependencies: `poetry update`
- Run commands in virtual environment: `poetry run <command>`

## Code Style Guidelines
- Follow PEP 8 conventions (enforced by Black and flake8)
- Use type hints consistently (imports from `typing` module)
- Use docstrings with Args/Returns/Raises sections
- Error handling: use custom exception classes in `converter.py`
- Class naming: CamelCase (e.g., `WebdownError`)
- Function naming: snake_case (e.g., `convert_url_to_markdown`)
- Imports order: standard lib, third-party, local modules (enforced by isort)
- Test classes: prefix with `Test` and use descriptive method names
- Mark integration tests with `@pytest.mark.integration`
- Format code with Black before committing
- Sort imports with isort before committing
- Pre-commit hooks will enforce code quality standards
