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
- Run all tests: `poetry run pytest` or `make test`
- Run specific test: `poetry run pytest webdown/tests/test_file.py::TestClass::test_function`
- Run with coverage: `poetry run pytest --cov=webdown` or `make test-coverage`
- Run integration tests: `poetry run pytest --integration` or `make integration-test`
- Type checking: `poetry run mypy webdown` or `make type-check`
- Linting: `poetry run flake8 webdown` or `make lint`
- Formatting: `poetry run black webdown && poetry run isort webdown` or `make format`
- All checks: `make all-checks`
- Building package: `poetry build` or `make build`

### Path-Independent Environment Management
- We use a path-independent approach that works regardless of where the repo is cloned
- Poetry is configured to create virtualenvs in-project: `poetry config virtualenvs.in-project true`
- Use `./scripts/run.sh <command>` to run any command in the correct environment
- Examples:
  - Run tests: `./scripts/run.sh pytest`
  - Run pre-commit: `./scripts/run.sh pre-commit run`
  - Run any other command: `./scripts/run.sh python -m webdown.cli`

### Virtual Environment Management
- Install dependencies: `poetry install`
- Run commands in virtual environment: `poetry run <command>` or `./scripts/run.sh <command>`
- Activate environment in fish shell: `source (poetry env activate --fish)`
- Activate environment in bash/zsh: `source $(poetry env activate)`
- Check environment info: `poetry env info`

### Pre-commit Setup
- Pre-commit is configured to use isolated environments via `default_language_version`
- Install hooks: `./scripts/run.sh pre-commit install` (only needed once)
- If pre-commit hooks need to be reinstalled:
  ```bash
  # Remove old hooks
  rm -f .git/hooks/pre-commit

  # Install hooks with our helper script
  ./scripts/run.sh pre-commit install
  ```

### Development with Poetry
- Add dependency: `poetry add requests`
- Add dev dependency: `poetry add --group dev pytest`
- Update dependencies: `poetry update`

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

### Function Design Guidelines
- Keep functions under 30 lines of executable code for improved readability (50 absolute max)
  - Comments and docstrings don't count toward line limits
- Limit parameters to 5 or fewer; use configuration objects for complex parameter sets
- Use underscore prefix for internal helper functions (e.g., `_validate_input`)
- Follow Single Responsibility Principle - each function should do one thing well
- Extract repeated code into dedicated helper functions
- Prefer early returns for validation to avoid deeply nested conditions
- Centralize validation logic rather than duplicating across functions
- Use configuration objects (like `WebdownConfig`, `ClaudeXMLConfig`) for consistent parameter handling
- Follow a "tell, don't ask" principle when designing function interactions
- Keep public API surface minimal and clearly documented
