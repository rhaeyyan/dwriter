"""Pytest configuration and fixtures."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_path():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture(autouse=True)
def mock_user_home(monkeypatch, temp_path):
    """Mock user home directory for all tests."""
    monkeypatch.setenv("HOME", str(temp_path))
