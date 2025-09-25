import pytest
from unittest.mock import patch, MagicMock
from jiboia.core.service.strategy.projects import SyncProjectsStrategy

@pytest.fixture
def mock_project_model(monkeypatch):
    class DummyProject:
        objects = MagicMock()
    monkeypatch.setattr('jiboia.core.models.Project', DummyProject)
    return DummyProject

def test_execute_projects(monkeypatch, mock_project_model):
    strategy = SyncProjectsStrategy('email', 'token', 'http://fake-jira')
    mock_response = MagicMock()
    mock_response.json.return_value = {"values": [{"id": "1", "key": "PRJ"}]}
    mock_response.raise_for_status = MagicMock()
    monkeypatch.setattr(strategy, '_make_request', lambda *a, **k: mock_response)
    result = strategy.execute()
    assert isinstance(result, int)
    assert result >= 0

    def test_execute_projects_empty(monkeypatch, mock_project_model):
        strategy = SyncProjectsStrategy('email', 'token', 'http://fake-jira')
        mock_response = MagicMock()
        mock_response.json.return_value = {"values": []}
        mock_response.raise_for_status = MagicMock()
        monkeypatch.setattr(strategy, '_make_request', lambda *a, **k: mock_response)
        result = strategy.execute()
        assert result == 0

    def test_execute_projects_exception(monkeypatch, mock_project_model):
        strategy = SyncProjectsStrategy('email', 'token', 'http://fake-jira')
        mock_response = MagicMock()
        mock_response.json.return_value = {"values": [{"id": "1", "key": "PRJ"}]}
        mock_response.raise_for_status = MagicMock()
        def update_or_create_fail(*a, **k):
            raise Exception("db error")
        mock_project_model.objects.update_or_create.side_effect = update_or_create_fail
        monkeypatch.setattr(strategy, '_make_request', lambda *a, **k: mock_response)
        result = strategy.execute()
        assert result == 0

    def test_execute_projects_missing_fields(monkeypatch, mock_project_model):
        strategy = SyncProjectsStrategy('email', 'token', 'http://fake-jira')
        mock_response = MagicMock()
        # Missing name and description
        mock_response.json.return_value = {"values": [{"id": "2", "key": "PRJ2"}]}
        mock_response.raise_for_status = MagicMock()
        monkeypatch.setattr(strategy, '_make_request', lambda *a, **k: mock_response)
        result = strategy.execute()
        assert isinstance(result, int)
