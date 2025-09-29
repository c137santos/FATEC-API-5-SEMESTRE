"""Tests for healthcheck strategies."""

from unittest.mock import patch

from jiboia.core.service.strategy.healthcheck import ProjectsHealthCheckStrategy


@patch('jiboia.core.service.strategy.base.requests.get')
def test_projects_healthcheck_success(mock_get, mock_response, projects_data):
    """Test successful projects healthcheck."""
    mock_response.status_code = 200
    mock_response.json.return_value = projects_data
    mock_get.return_value = mock_response

    strategy = ProjectsHealthCheckStrategy('test@example.com', 'token123', 'https://jira.example.com')
    success, message = strategy.execute()

    assert success is True
    assert f"OK - {len(projects_data)} projects found" in message
    mock_get.assert_called_once()


@patch('jiboia.core.service.strategy.base.requests.get')
def test_projects_healthcheck_empty_response(mock_get, mock_response):
    """Test projects healthcheck with empty response."""
    mock_response.status_code = 200
    mock_response.json.return_value = []
    mock_get.return_value = mock_response

    strategy = ProjectsHealthCheckStrategy('test@example.com', 'token123', 'https://jira.example.com')
    success, message = strategy.execute()

    assert success is True
    assert "OK - 0 projects found" in message
    mock_get.assert_called_once()


@patch('jiboia.core.service.strategy.base.requests.get')
def test_projects_healthcheck_http_error(mock_get, mock_response):
    """Test projects healthcheck with HTTP error."""
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    mock_get.return_value = mock_response

    strategy = ProjectsHealthCheckStrategy('test@example.com', 'token123', 'https://jira.example.com')
    success, message = strategy.execute()

    assert success is False
    assert "Failed with status 401" in message
    mock_get.assert_called_once()


@patch('jiboia.core.service.strategy.base.requests.get')
def test_projects_healthcheck_exception(mock_get):
    """Test projects healthcheck with exception."""
    mock_get.side_effect = Exception("Connection error")

    strategy = ProjectsHealthCheckStrategy('test@example.com', 'token123', 'https://jira.example.com')
    success, message = strategy.execute()

    assert success is False
    assert "Connection error" in message
    mock_get.assert_called_once()