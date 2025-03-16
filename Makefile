.PHONY: install install-dev test lint type-check clean all-checks integration-test test-coverage format lock update docs docs-serve publish publish-test release

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
	$(POETRY) run mkdocs build

docs-serve:
	$(POETRY) run mkdocs serve

docs-deploy:
	$(POETRY) run mkdocs gh-deploy --force

shell:
	@echo "Starting Poetry shell..."
	@$(POETRY) shell

publish-test: clean build
	@echo "Publishing package to TestPyPI..."
	@$(POETRY) config repositories.testpypi https://test.pypi.org/legacy/
	@$(POETRY) publish --repository testpypi

publish: clean all-checks build
	@echo "NOTICE: For production PyPI publishing, use the GitHub Actions workflow by tagging a release."
	@echo "See CONTRIBUTING.md for the release process."
	@echo ""
	@echo "This command is for emergency manual publishing only."
	@echo "Are you sure you want to publish directly to PyPI? [y/N] "
	@read -r response; \
	if [ "$$response" = "y" ] || [ "$$response" = "Y" ]; then \
		echo "Publishing package to PyPI..."; \
		$(POETRY) publish; \
	else \
		echo "Publishing aborted."; \
	fi

release: all-checks build
	@echo "Preparing release process..."

	@echo "Verifying version consistency..."
	@VERSION=$$(grep -oP '^version = "\K[^"]+' pyproject.toml); \
	INIT_VERSION=$$(grep -oP '__version__ = "\K[^"]+' webdown/__init__.py); \
	if [ "$$VERSION" != "$$INIT_VERSION" ]; then \
		echo "Error: Version mismatch! pyproject.toml ($$VERSION) vs __init__.py ($$INIT_VERSION)"; \
		exit 1; \
	fi; \
	echo "Version $$VERSION is consistent across files."

	@echo "Checking for CHANGELOG.md entry..."
	@VERSION=$$(grep -oP '^version = "\K[^"]+' pyproject.toml); \
	if ! grep -q "## \[$$VERSION\]" CHANGELOG.md; then \
		echo "Error: No entry for version $$VERSION found in CHANGELOG.md"; \
		exit 1; \
	fi; \
	echo "CHANGELOG.md entry found."

	@echo "Creating release tag..."
	@VERSION=$$(grep -oP '^version = "\K[^"]+' pyproject.toml); \
	echo "Ready to tag release v$$VERSION and trigger GitHub Actions release workflow."; \
	echo "Are you sure you want to continue? [y/N] "; \
	read -r response; \
	if [ "$$response" = "y" ] || [ "$$response" = "Y" ]; then \
		git tag -a "v$$VERSION" -m "Release version $$VERSION"; \
		echo "Tag v$$VERSION created locally."; \
		echo "To finish the release, run: git push origin v$$VERSION"; \
		echo "This will trigger the GitHub Actions workflow to publish to PyPI."; \
	else \
		echo "Release tagging aborted."; \
	fi

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
	@echo "  docs            Generate documentation with MkDocs"
	@echo "  docs-serve      Start a local MkDocs documentation server at http://localhost:8000"
	@echo "  docs-deploy     Deploy documentation to GitHub Pages"
	@echo "  publish-test    Publish package to TestPyPI (test.pypi.org)"
	@echo "  publish         Emergency manual publishing to PyPI (normally done via GitHub Actions)"
	@echo "  release         Prepare and tag a new release (runs checks, verifies versions, creates git tag)"
	@echo "  help            Show this help message"
