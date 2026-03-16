"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def anyio_backend():
    """Use asyncio as the async backend for pytest-anyio."""
    return "asyncio"


# Configure pytest-asyncio
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers",
        "asyncio: mark test as async",
    )
