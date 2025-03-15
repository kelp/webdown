.PHONY: install test lint type-check clean all-checks integration-test test-coverage format lock update

# Use Poetry for all commands
POETRY := poetry
POETRY_RUN := $(POETRY) run

install:
	@echo "Installing package and dependencies with Poetry..."
	@$(POETRY) install
	@$(POETRY_RUN) pre-commit install

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
	@$(POETRY_RUN) flake8 webdown

type-check:
	@echo "Running type checker..."
	@$(POETRY_RUN) mypy webdown

format:
	@echo "Formatting code..."
	@$(POETRY_RUN) black webdown
	@$(POETRY_RUN) isort webdown

pre-commit:
	@echo "Running pre-commit hooks on all files..."
	@$(POETRY_RUN) pre-commit run --all-files

all-checks: lint type-check test
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
	@echo "  pre-commit      Run pre-commit hooks on all files"
	@echo "  all-checks      Run linting, type checking, and tests"
	@echo "  build           Build package for distribution"
	@echo "  lock            Update lock file (poetry.lock)"
	@echo "  update          Update dependencies"
	@echo "  clean           Remove build artifacts and caches"
	@echo "  shell           Start Poetry shell (interactive environment)"
	@echo "  help            Show this help message"
