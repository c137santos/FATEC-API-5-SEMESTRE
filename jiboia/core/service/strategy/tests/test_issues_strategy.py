from datetime import date, datetime
from unittest.mock import MagicMock

import pytest
import requests

import jiboia.core.service.strategy.issues as issues_mod
from jiboia.core.service.strategy.issues import SyncIssuesStrategy


def test_update_project_dates(monkeypatch):
    # Mock Project e issues
    class DummyIssue:
        def __init__(self, start, end):
            self.start_date = start
            self.end_date = end

    class DummyQuerySet:
        def __init__(self, issues):
            self._issues = issues

        def all(self):
            return self

        def aggregate(self, agg):
            # agg pode ser Min('start_date') ou Max('end_date')
            from django.db.models import Max, Min

            if isinstance(agg, Min):
                return {"start_date__min": min((i.start_date for i in self._issues if i.start_date), default=None)}
            if isinstance(agg, Max):
                return {"end_date__max": max((i.end_date for i in self._issues if i.end_date), default=None)}
            return {}

    class DummyProject:
        def __init__(self):
            self.start_date_project = None
            self.end_date_project = None
            self.saved = False
            self.issue_set = DummyQuerySet(
                [
                    DummyIssue(datetime(2023, 1, 1), datetime(2023, 1, 10)),
                    DummyIssue(datetime(2023, 1, 5), datetime(2023, 1, 20)),
                    DummyIssue(None, None),
                ]
            )

        def save(self):
            self.saved = True

    project = DummyProject()
    SyncIssuesStrategy.update_project_dates(project)
    assert project.start_date_project == date(2023, 1, 1)
    assert project.end_date_project == date(2023, 1, 20)
    assert project.saved


@pytest.fixture
def test_execute_issues(monkeypatch, mock_issue_model):
    strategy = SyncIssuesStrategy("email", "token", "http://fake-jira")
    mock_response = MagicMock()
    mock_response.json.return_value = {"issues": [], "total": 0}
    mock_response.raise_for_status = MagicMock()
    monkeypatch.setattr(strategy, "_make_request", lambda *a, **k: mock_response)
    dummy_project = MagicMock()
    issues_mod.Project = MagicMock()
    issues_mod.Project.objects.get.return_value = dummy_project
    monkeypatch.setattr(strategy, "_sync_issue", lambda *a, **k: MagicMock())
    monkeypatch.setattr(strategy, "_sync_worklogs", lambda *a, **k: None)
    monkeypatch.setattr(requests, "get", lambda *a, **k: mock_response)
    result = strategy.execute("PRJ")
    assert isinstance(result, int)
    assert result >= 0
