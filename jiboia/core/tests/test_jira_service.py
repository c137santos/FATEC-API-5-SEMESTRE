from unittest.mock import MagicMock, patch

from requests.exceptions import ConnectionError, Timeout

from jiboia.core.service.jira_svc import JiraService


class TestJiraService:

    @patch('jiboia.core.service.jira_svc.requests.get')
    def test_healthcheck_success(self, mock_get):
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

    @patch('jiboia.core.service.jira_svc.requests.get')
    def test_healthcheck_empty_response(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        success, message = JiraService.healthcheck()

        assert success is True
        assert "OK - 0 projects found" in message
        mock_get.assert_called_once()

    @patch('jiboia.core.service.jira_svc.requests.get')
    def test_healthcheck_http_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response

        success, message = JiraService.healthcheck()

        assert success is False
        assert "Failed with status 401" in message
        mock_get.assert_called_once()

    @patch('jiboia.core.service.jira_svc.requests.get')
    def test_healthcheck_server_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response

        success, message = JiraService.healthcheck()

        assert success is False
        assert "Failed with status 500" in message
        mock_get.assert_called_once()

    @patch('jiboia.core.service.jira_svc.requests.get')
    def test_healthcheck_connection_error(self, mock_get):
        mock_get.side_effect = ConnectionError("Connection failure")

        success, message = JiraService.healthcheck()

        assert success is False
        assert "Connection failure" in message
        mock_get.assert_called_once()

    @patch('jiboia.core.service.jira_svc.requests.get')
    def test_healthcheck_timeout(self, mock_get):
        mock_get.side_effect = Timeout("Request timeout")

        success, message = JiraService.healthcheck()

        assert success is False
        assert "Request timeout" in message
        mock_get.assert_called_once()

    @patch('jiboia.core.service.jira_svc.requests.get')
    def test_healthcheck_generic_exception(self, mock_get):
        mock_get.side_effect = Exception("Unexpected error")

        success, message = JiraService.healthcheck()

        assert success is False
        assert "Unexpected error" in message
        mock_get.assert_called_once()