import pytest
from unittest.mock import patch, MagicMock
from jiboia.core.service.strategy.issue_types import SyncIssueTypesStrategy

@pytest.fixture
def mock_issue_type_model(monkeypatch):
    class DummyIssueType:
        objects = MagicMock()
    monkeypatch.setattr('jiboia.core.models.IssueType', DummyIssueType)
    return DummyIssueType

def test_execute_issue_types(monkeypatch, mock_issue_type_model):
    strategy = SyncIssueTypesStrategy('email', 'token', 'http://fake-jira')
    mock_response = MagicMock()
    mock_response.json.return_value = [{"id": "1", "name": "Bug"}]
    mock_response.raise_for_status = MagicMock()
    monkeypatch.setattr(strategy, '_make_request', lambda *a, **k: mock_response)
    result = strategy.execute()
    assert isinstance(result, int)
    assert result >= 0
