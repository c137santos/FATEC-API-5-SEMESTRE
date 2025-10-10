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

def test_sync_issue_data(sync_issues_strategy_setup, jira_issue_data_page1):
    """Testa a sincronização de uma única issue e mapeamento de campos."""
    strategy = sync_issues_strategy_setup
    project = strategy.Project(key="PRJ") 
    
    issue_obj = strategy._sync_issue(jira_issue_data_page1["issues"][0], project)

    assert issue_obj is not None
    assert issue_obj.jira_id == "10001"
    assert issue_obj.id_user.username == "user123"
    assert issue_obj.description == "Issue Test"
    assert issue_obj.details == "Detalhes da Issue"


def test_sync_worklogs_data(sync_issues_strategy_setup, jira_issue_data_page1):
    """Testa a sincronização dos worklogs e o helper de comentário."""
    strategy = sync_issues_strategy_setup
    issue = strategy.Issue(jira_id="10001")
    
    strategy._sync_worklogs(issue, jira_issue_data_page1["issues"][0])
    
    log_data = jira_issue_data_page1["issues"][0]["fields"]["worklog"]["worklogs"][0]
    comment = log_data["comment"]
    assert strategy._get_worklog_comment_text(comment) == "Worklog Test"


def test_execute_main_sync(monkeypatch, sync_issues_strategy_setup, jira_issue_data_page1, jira_issue_data_page_empty):
    """Testa o fluxo principal de sincronização paginada e contagem."""
    strategy = sync_issues_strategy_setup
    
    def mock_requests_get(*args, **kwargs):
        params = kwargs.get('params', {})
        start_at = params.get('startAt', 0)
        
        if start_at == 0:
            response = MagicMock(status_code=200)
            response.json.return_value = jira_issue_data_page1
            return response
        else:
            response = MagicMock(status_code=200)
            response.json.return_value = jira_issue_data_page_empty
            return response

    monkeypatch.setattr(requests, "get", mock_requests_get)
    
    project_instance = strategy.Project(key='PRJ')
    def mock_project_get(**kwargs):
        if kwargs.get('key') == 'PRJ':
            return project_instance
        raise issues_mod.Project.DoesNotExist

    issues_mod.Project.objects.get = mock_project_get
    
    synced_issues = 0
    def mock_sync_issue(issue_data, project):
        nonlocal synced_issues
        synced_issues += 1
        return strategy.Issue(jira_id=issue_data['id'])
        
    def mock_sync_worklogs(issue_obj, issue_data):
        # Função intencionalmente vazia (mock) para ser usada em testes.
        # Evita a sincronização real durante a execução dos testes.
        pass

    monkeypatch.setattr(strategy, "_sync_issue", mock_sync_issue)
    monkeypatch.setattr(strategy, "_sync_worklogs", mock_sync_worklogs)

    synced_count = strategy.execute("PRJ")
    
    assert synced_count == 1
    assert synced_issues == 1
    assert project_instance.saved is True