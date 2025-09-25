import pytest
from unittest.mock import patch, MagicMock
from jiboia.core.service.strategy.status_types import SyncStatusTypesStrategy

@pytest.fixture
def mock_status_type_model(monkeypatch):
    class DummyStatusType:
        objects = MagicMock()
    monkeypatch.setattr('jiboia.core.models.StatusType', DummyStatusType)
    return DummyStatusType

def test_execute_status_types(monkeypatch, mock_status_type_model):
    strategy = SyncStatusTypesStrategy('email', 'token', 'http://fake-jira')
    mock_response = MagicMock()
    mock_response.json.return_value = [{"id": "1", "name": "To Do", "statusCategory": {"key": "new"}}]
    mock_response.raise_for_status = MagicMock()
    monkeypatch.setattr(strategy, '_make_request', lambda *a, **k: mock_response)
    result = strategy.execute()
    assert isinstance(result, int)
    assert result >= 0

def test_execute_status_types_empty(monkeypatch, mock_status_type_model):
    strategy = SyncStatusTypesStrategy('email', 'token', 'http://fake-jira')
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_response.raise_for_status = MagicMock()
    monkeypatch.setattr(strategy, '_make_request', lambda *a, **k: mock_response)
    result = strategy.execute()
    assert result == 0

def test_execute_status_types_exception(monkeypatch, mock_status_type_model):
    strategy = SyncStatusTypesStrategy('email', 'token', 'http://fake-jira')
    mock_response = MagicMock()
    mock_response.json.return_value = [{"id": "1", "name": "To Do", "statusCategory": {"key": "new"}}]
    mock_response.raise_for_status = MagicMock()
    def update_or_create_fail(*a, **k):
        raise Exception("db error")
    mock_status_type_model.objects.update_or_create.side_effect = update_or_create_fail
    monkeypatch.setattr(strategy, '_make_request', lambda *a, **k: mock_response)
    result = strategy.execute()
    assert result == 0

def test_execute_status_types_missing_fields(monkeypatch, mock_status_type_model):
    strategy = SyncStatusTypesStrategy('email', 'token', 'http://fake-jira')
    mock_response = MagicMock()
    # Missing statusCategory
    mock_response.json.return_value = [{"id": "2", "name": "In Progress"}]
    mock_response.raise_for_status = MagicMock()
    monkeypatch.setattr(strategy, '_make_request', lambda *a, **k: mock_response)
    result = strategy.execute()
    assert isinstance(result, int)
