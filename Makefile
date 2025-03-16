.PHONY: install install-dev test lint type-check clean all-checks integration-test test-coverage format lock update docs docs-serve

# Use Poetry for all commands
POETRY := poetry
POETRY_RUN := $(POETRY) run

install:
	@echo "Installing package and dependencies with Poetry..."
	@$(POETRY) install
	@$(POETRY_RUN) pre-commit install

install-dev:
	@echo "Installing package for current user in development mode..."
	@$(POETRY) install
	@$(POETRY) build
	@pip install --user -e .
	@echo "✓ Installed webdown in development mode for current user"

test:
	@echo "Running tests..."
	@$(POETRY_RUN) pytest

test-coverage:
	@echo "Running tests with coverage..."
	@$(POETRY_RUN) pytest --cov=webdown

integration-test:
	@echo "Running integration tests..."
	@$(POETRY_RUN) pytest --integration

lint:
	@echo "Running linter..."
	@$(POETRY_RUN) flake8 webdown conftest.py

type-check:
	@echo "Running type checker..."
	@$(POETRY_RUN) mypy webdown conftest.py

format:
	@echo "Formatting code..."
	@$(POETRY_RUN) black webdown conftest.py
	@$(POETRY_RUN) isort webdown conftest.py

pre-commit:
	@echo "Running pre-commit hooks on all files..."
	@$(POETRY_RUN) pre-commit run --all-files

format-check:
	@echo "Checking code formatting..."
	@$(POETRY_RUN) black --check webdown conftest.py
	@$(POETRY_RUN) isort --check webdown conftest.py

all-checks: format-check lint type-check test
	@echo "All checks passed!"

build:
	@echo "Building package..."
	@$(POETRY) build

lock:
	@echo "Updating lock file..."
	@$(POETRY) lock

update:
	@echo "Updating dependencies..."
	@$(POETRY) update

clean:
	@echo "Cleaning up..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

# Documentation
docs:
	$(POETRY) run pdoc webdown -o docs

docs-serve:
	$(POETRY) run pdoc -h localhost -p 8080 webdown

shell:
	@echo "Starting Poetry shell..."
	@$(POETRY) shell

help:
	@echo "Available targets:"
	@echo "  install         Install package and dependencies with Poetry"
	@echo "  test            Run unit tests"
	@echo "  test-coverage   Run tests with coverage report"
	@echo "  integration-test Run integration tests"
	@echo "  lint            Run flake8 linter"
	@echo "  type-check      Run mypy type checking"
	@echo "  format          Format code with black and isort"
	@echo "  format-check    Check code formatting with black and isort without modifying files"
	@echo "  pre-commit      Run pre-commit hooks on all files"
	@echo "  all-checks      Run format checks, linting, type checking, and tests"
	@echo "  build           Build package for distribution"
	@echo "  lock            Update lock file (poetry.lock)"
	@echo "  update          Update dependencies"
	@echo "  clean           Remove build artifacts and caches"
	@echo "  shell           Start Poetry shell (interactive environment)"
	@echo "  install-dev     Install package for current user in development mode"
	@echo "  docs            Generate HTML documentation with pdoc"
	@echo "  docs-serve      Start a local documentation server at http://localhost:8080"
	@echo "  help            Show this help message"
