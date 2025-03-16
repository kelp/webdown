"""Configuration for pytest."""

from typing import Any


def pytest_configure(config: Any) -> None:
    """Configure pytest with integration marker."""
    config.addinivalue_line("markers", "integration: mark tests as integration tests")
