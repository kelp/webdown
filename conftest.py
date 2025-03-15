"""Pytest configuration for webdown."""

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add command-line options to pytest."""
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="run integration tests",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest."""
    config.addinivalue_line("markers", "integration: mark test as integration test")


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Skip tests based on markers."""
    if not config.getoption("--integration"):
        skip_integration = pytest.mark.skip(reason="need --integration option to run")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)
