from unittest.mock import MagicMock

from jiboia.core.service.strategy.healthcheck import ProjectsHealthCheckStrategy


def test_execute_healthcheck(monkeypatch):
    strategy = ProjectsHealthCheckStrategy('email', 'token', 'http://fake-jira')
    mock_response = MagicMock()
    mock_response.json.return_value = {}
    mock_response.raise_for_status = MagicMock()
    monkeypatch.setattr(strategy, '_make_request', lambda *a, **k: mock_response)
    success, message = strategy.execute()
    assert isinstance(success, bool)
    assert isinstance(message, str)
