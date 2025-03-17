.PHONY: install install-dev test lint type-check clean all-checks integration-test test-coverage format lock update docs docs-serve publish publish-test release

# Path-independent environment setup
SCRIPT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
RUN_SCRIPT := $(SCRIPT_DIR)/scripts/run.sh

# Use Poetry for all commands
POETRY := poetry
POETRY_RUN := $(RUN_SCRIPT)

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
	@VERSION=$$(grep '^version =' pyproject.toml | sed 's/version = "//;s/"//'); \
	INIT_VERSION=$$(grep '__version__ =' webdown/__init__.py | sed 's/__version__ = "//;s/"//'); \
	if [ "$$VERSION" != "$$INIT_VERSION" ]; then \
		echo "Error: Version mismatch! pyproject.toml ($$VERSION) vs __init__.py ($$INIT_VERSION)"; \
		exit 1; \
	fi; \
	echo "Version $$VERSION is consistent across files."

	@echo "Checking for CHANGELOG.md entry..."
	@VERSION=$$(grep '^version =' pyproject.toml | sed 's/version = "//;s/"//'); \
	if ! grep -q "## \[$$VERSION\]" CHANGELOG.md; then \
		echo "Error: No entry for version $$VERSION found in CHANGELOG.md"; \
		exit 1; \
	fi; \
	echo "CHANGELOG.md entry found."

	@echo "Creating release tag..."
	@VERSION=$$(grep '^version =' pyproject.toml | sed 's/version = "//;s/"//'); \
	if [ "$(CONFIRM)" = "yes" ]; then \
		git tag -a "v$$VERSION" -m "Release version $$VERSION"; \
		echo "Tag v$$VERSION created locally."; \
		echo "To finish the release, run: git push origin v$$VERSION"; \
		echo "This will trigger the GitHub Actions workflow to publish to PyPI."; \
	else \
		echo "Ready to tag release v$$VERSION and trigger GitHub Actions release workflow."; \
		echo "To create the release tag, run: make release CONFIRM=yes"; \
		echo "To finish the release, run: git push origin v$$VERSION"; \
	fi

# This is a variant that skips the confirmation prompt
release-auto: all-checks build
	@echo "Preparing release process..."
	@VERSION=$$(grep '^version =' pyproject.toml | sed 's/version = "//;s/"//'); \
	INIT_VERSION=$$(grep '__version__ =' webdown/__init__.py | sed 's/__version__ = "//;s/"//'); \
	if [ "$$VERSION" != "$$INIT_VERSION" ]; then \
		echo "Error: Version mismatch! pyproject.toml ($$VERSION) vs __init__.py ($$INIT_VERSION)"; \
		exit 1; \
	fi; \
	echo "Version $$VERSION is consistent across files."; \
	if ! grep -q "## \[$$VERSION\]" CHANGELOG.md; then \
		echo "Error: No entry for version $$VERSION found in CHANGELOG.md"; \
		exit 1; \
	fi; \
	echo "CHANGELOG.md entry found."; \
	git tag -a "v$$VERSION" -m "Release version $$VERSION"; \
	echo "Tag v$$VERSION created successfully."; \
	echo "To finish the release, run: git push origin v$$VERSION";

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
	@echo "  release         Prepare for a new release (runs checks, verifies versions)"
	@echo "  release CONFIRM=yes  Create a release tag without prompting"
	@echo "  release-auto    Non-interactive version that creates the release tag automatically"
	@echo "  help            Show this help message"
