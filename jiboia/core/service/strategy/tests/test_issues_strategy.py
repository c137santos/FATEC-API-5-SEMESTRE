from unittest.mock import MagicMock

import pytest

from jiboia.core.service.strategy.issues import SyncIssuesStrategy
import jiboia.core.service.strategy.issues as issues_mod
import requests


@pytest.fixture
def mock_issue_model(monkeypatch):
    class DummyIssue:
        objects = MagicMock()
    monkeypatch.setattr('jiboia.core.models.Issue', DummyIssue)
    class DummyProject:
        objects = MagicMock()
    monkeypatch.setattr('jiboia.core.models.Project', DummyProject)
    return DummyIssue, DummyProject

def test_execute_issues(monkeypatch, mock_issue_model):
    strategy = SyncIssuesStrategy('email', 'token', 'http://fake-jira')
    mock_response = MagicMock()
    mock_response.json.return_value = {"issues": [], "total": 0}
    mock_response.raise_for_status = MagicMock()
    monkeypatch.setattr(strategy, '_make_request', lambda *a, **k: mock_response)
    dummy_project = MagicMock()
    issues_mod.Project = MagicMock()
    issues_mod.Project.objects.get.return_value = dummy_project
    monkeypatch.setattr(strategy, '_sync_issue', lambda *a, **k: MagicMock())
    monkeypatch.setattr(strategy, '_sync_worklogs', lambda *a, **k: None)
    monkeypatch.setattr(strategy, '_sync_status_logs', lambda *a, **k: None)
    monkeypatch.setattr(requests, 'get', lambda *a, **k: mock_response)
    result = strategy.execute('PRJ')
    assert isinstance(result, int)
    assert result >= 0
