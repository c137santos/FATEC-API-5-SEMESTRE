from unittest.mock import MagicMock, patch

from requests.exceptions import ConnectionError, Timeout

from jiboia.core.service.jira_svc import JiraService


@patch('jiboia.core.service.strategy.base.requests.get')
def test_healthcheck_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"id": "10000", "key": "PROJ1", "name": "Projeto 1"},
        {"id": "10001", "key": "PROJ2", "name": "Projeto 2"}
    ]
    mock_get.return_value = mock_response

    success, message = JiraService.healthcheck()

    assert success is True
    assert "OK - 2 projects found" in message
    mock_get.assert_called_once()


@patch('jiboia.core.service.strategy.base.requests.get')
def test_healthcheck_empty_response(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = []
    mock_get.return_value = mock_response

    success, message = JiraService.healthcheck()

    assert success is True
    assert "OK - 0 projects found" in message
    mock_get.assert_called_once()


@patch('jiboia.core.service.strategy.base.requests.get')
def test_healthcheck_http_error(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    mock_get.return_value = mock_response

    success, message = JiraService.healthcheck()

    assert success is False
    assert "Failed with status 401" in message
    mock_get.assert_called_once()


@patch('jiboia.core.service.strategy.base.requests.get')
def test_healthcheck_server_error(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_get.return_value = mock_response

    success, message = JiraService.healthcheck()

    assert success is False
    assert "Failed with status 500" in message
    mock_get.assert_called_once()


@patch('jiboia.core.service.strategy.base.requests.get')
def test_healthcheck_connection_error(mock_get):
    mock_get.side_effect = ConnectionError("Connection failure")

    success, message = JiraService.healthcheck()

    assert success is False
    assert "Connection failure" in message
    mock_get.assert_called_once()


@patch('jiboia.core.service.strategy.base.requests.get')
def test_healthcheck_timeout(mock_get):
    mock_get.side_effect = Timeout("Request timeout")

    success, message = JiraService.healthcheck()

    assert success is False
    assert "Request timeout" in message
    mock_get.assert_called_once()


@patch('jiboia.core.service.strategy.base.requests.get')
def test_healthcheck_generic_exception(mock_get):
    mock_get.side_effect = Exception("Unexpected error")

    success, message = JiraService.healthcheck()

    assert success is False
    assert "Unexpected error" in message
    mock_get.assert_called_once()


@patch('jiboia.core.service.strategy.projects.ProjectsApiStrategy.save_projects')
@patch('jiboia.core.service.strategy.projects.ProjectsApiStrategy.process')
@patch('jiboia.core.service.strategy.projects.ProjectsApiStrategy.execute')
def test_get_projects_success(mock_execute, mock_process, mock_save_projects):
    mock_execute.return_value = [
        {"id": "10000", "key": "PROJ1", "name": "Projeto 1"},
        {"id": "10001", "key": "PROJ2", "name": "Projeto 2"}
    ]
    mock_process.return_value = [
        {"jira_id": "10000", "name": "Projeto 1"},
        {"jira_id": "10001", "name": "Projeto 2"}
    ]
    mock_save_projects.return_value = ["Projeto 1", "Projeto 2"]

    result = JiraService.get_projects()

    assert result == ["Projeto 1", "Projeto 2"]
    mock_execute.assert_called_once()
    mock_process.assert_called_once_with(mock_execute.return_value)
    mock_save_projects.assert_called_once_with(mock_process.return_value)

@patch('jiboia.core.service.strategy.projects.ProjectsApiStrategy.save_projects')
@patch('jiboia.core.service.strategy.projects.ProjectsApiStrategy.process')
@patch('jiboia.core.service.strategy.projects.ProjectsApiStrategy.execute')
def test_get_projects_empty(mock_execute, mock_process, mock_save_projects):
    mock_execute.return_value = []
    mock_process.return_value = []
    mock_save_projects.return_value = []

    result = JiraService.get_projects()

    assert result == []
    mock_execute.assert_called_once()
    mock_process.assert_called_once_with([])
    mock_save_projects.assert_called_once_with([])

@patch('jiboia.core.service.strategy.projects.ProjectsApiStrategy.save_projects')
@patch('jiboia.core.service.strategy.projects.ProjectsApiStrategy.process')
@patch('jiboia.core.service.strategy.projects.ProjectsApiStrategy.execute')
def test_get_projects_api_error(mock_execute, mock_process, mock_save_projects):
    mock_execute.side_effect = Exception("API error")

    try:
        JiraService.get_projects()
        assert False, "Exception not raised"
    except Exception as e:
        assert "API error" in str(e)
    mock_execute.assert_called_once()
    mock_process.assert_not_called()
    mock_save_projects.assert_not_called()

@patch('jiboia.core.service.strategy.projects.ProjectsApiStrategy.save_projects')
@patch('jiboia.core.service.strategy.projects.ProjectsApiStrategy.process')
@patch('jiboia.core.service.strategy.projects.ProjectsApiStrategy.execute')
def test_get_projects_success_called(mock_execute, mock_process, mock_save_projects):
    mock_execute.return_value = [
        {"id": "10000", "key": "PROJ1", "name": "Projeto 1"},
        {"id": "10001", "key": "PROJ2", "name": "Projeto 2"}
    ]
    mock_process.return_value = [
        {"jira_id": "10000", "name": "Projeto 1"},
        {"jira_id": "10001", "name": "Projeto 2"}
    ]
    mock_save_projects.return_value = ["Projeto 1", "Projeto 2"]

    result = JiraService.get_projects()

    assert result == ["Projeto 1", "Projeto 2"]
    mock_execute.assert_called_once()
    mock_process.assert_called_once_with(mock_execute.return_value)
    mock_save_projects.assert_called_once_with(mock_process.return_value)