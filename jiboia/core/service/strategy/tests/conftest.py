"""Pytest configuration for strategy tests."""

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_response():
    """Create a mock response object."""
    response = MagicMock()
    return response


@pytest.fixture
def projects_data():
    """Sample projects data."""
    return [
        {"id": "10000", "key": "PROJ1", "name": "Project 1"},
        {"id": "10001", "key": "PROJ2", "name": "Project 2"},
        {"id": "10002", "key": "PROJ3", "name": "Project 3"}
    ]