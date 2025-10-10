from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest
import requests
from django.contrib.auth import get_user_model
from django.utils import timezone

from jiboia.core.models import Issue, IssueType, Project, StatusType, TimeLog
from jiboia.core.service.strategy.issues import SyncIssuesStrategy


@pytest.mark.django_db
def test_update_project_dates():
    """Testa a atualização das datas do projeto baseado nas issues"""
    project = Project.objects.create(
        jira_id=12345,
        key="TEST",
        name="Test Project",
        start_date_project=None,
        end_date_project=None
    )
    
    Issue.objects.create(
        project=project,
        jira_id=1,
        description="Issue 1",
        start_date=timezone.make_aware(datetime(2023, 1, 1)),
        end_date=timezone.make_aware(datetime(2023, 1, 10))
    )
    Issue.objects.create(
        project=project,
        jira_id=2, 
        description="Issue 2",
        start_date=timezone.make_aware(datetime(2023, 1, 5)),
        end_date=timezone.make_aware(datetime(2023, 1, 20))
    )
    Issue.objects.create(
        project=project,
        jira_id=3,
        description="Issue 3",
        start_date=None,
        end_date=None
    )
    
    SyncIssuesStrategy.update_project_dates(project)
    
    project.refresh_from_db()
    
    assert project.start_date_project == date(2023, 1, 1)
    assert project.end_date_project == date(2023, 1, 20)

@pytest.mark.django_db
def test_execute_sync_issues_integration():
    """Versão mais integrada - removendo mocks internos"""
    strategy = SyncIssuesStrategy("email", "token", "http://fake-jira")
    
    project = Project.objects.create(jira_id=12345, key="PRJ", name="Test Project")
    IssueType.objects.create(jira_id=1, name="Bug")
    StatusType.objects.create(jira_id=1, name="To Do")
    
    mock_response = {
        "total": 1,
        "issues": [{
            "id": "10001",  
            "fields": {
                "summary": "Test Issue",
                "description": None,
                "assignee": None,
                "issuetype": {"id": "1"},
                "status": {"id": "1"},
                "created": "2023-01-01T00:00:00.000Z",
                "resolutiondate": None,
                "customfield_10015": None,
                "timeestimate": None,
                "worklog": {"worklogs": []}
            }
        }]
    }
    
    with patch('requests.get') as mock_get, \
         patch('jiboia.core.service.strategy.users.SyncUserStrategy.execute', return_value=None):
        
        mock_get.return_value.json.return_value = mock_response
        
        synced_count = strategy.execute("PRJ")
        
        assert synced_count == 1
        
        issue = Issue.objects.get(project=project)
        assert issue.jira_id == 10001
        assert issue.description == "Test Issue"

@pytest.mark.django_db
def test_sync_worklogs_creation():
    """Testa a sincronização de worklogs"""
    strategy = SyncIssuesStrategy("email", "token", "http://fake-jira")
    
    project = Project.objects.create(
        jira_id=12345,
        key="PRJ",
        name="Test Project"
    )
    
    issue = Issue.objects.create(
        project=project,
        jira_id=10001,
        description="Test Issue"
    )
    
    worklog_data = {
        "id": "10001",
        "fields": {
            "worklog": {
                "worklogs": [
                    {
                        "id": "20001",  
                        "author": {"accountId": "user123"},
                        "timeSpentSeconds": 7200,
                        "started": "2023-01-01T10:00:00.000Z",
                        "comment": {
                            "content": [
                                {
                                    "content": [
                                        {"text": "Worklog Test"}
                                    ]
                                }
                            ]
                        }
                    }
                ]
            }
        }
    }
    
    def mock_sync_user_execute(*args, **kwargs):
        try:
            if args and hasattr(args[0], 'get') and callable(getattr(args[0], 'get')):
                user_data = args[0]
                account_id = user_data.get("accountId", "user123")
            elif kwargs and 'user_data' in kwargs:
                user_data = kwargs['user_data']
                account_id = user_data.get("accountId", "user123")
            else:
                account_id = "user123"
        except (AttributeError, IndexError, TypeError):
            account_id = "user123"
        
        user = get_user_model()
        new_user, _ = user.objects.get_or_create(
            username=account_id,
            defaults={"email": f"{account_id}@test.com"}
        )
        return new_user
    
    with patch('jiboia.core.service.strategy.users.SyncUserStrategy.execute', mock_sync_user_execute):
        strategy._sync_worklogs(issue, worklog_data)
        
        worklog = TimeLog.objects.get(jira_id=20001)
        assert worklog.id_issue == issue
        assert worklog.seconds == 7200
        assert worklog.description_log == "Worklog Test"

@pytest.mark.django_db
def test_sync_issue_without_assignee():
    """Testa a sincronização de issue sem assignee"""
    strategy = SyncIssuesStrategy("email", "token", "http://fake-jira")
    
    project = Project.objects.create(
        jira_id=12345,
        key="PRJ", 
        name="Test Project"
    )
    IssueType.objects.create(jira_id=1, name="Bug")
    StatusType.objects.create(jira_id=1, name="To Do")
    
    issue_data = {
        "id": "10003",  
        "fields": {
            "summary": "Issue Without Assignee",
            "description": None,
            "assignee": None, 
            "issuetype": {"id": "1"},
            "status": {"id": "1"},
            "created": "2023-01-01T00:00:00.000Z",
            "resolutiondate": None,
            "customfield_10015": None,
            "timeestimate": None
        }
    }
    
    mock_sync_user_execute = MagicMock()
    
    with patch('jiboia.core.service.strategy.users.SyncUserStrategy.execute', mock_sync_user_execute):
        issue_obj = strategy._sync_issue(issue_data, project)
        
        mock_sync_user_execute.assert_not_called()
        
        assert issue_obj is not None
        assert int(issue_obj.jira_id) == 10003
        assert issue_obj.description == "Issue Without Assignee"
        assert issue_obj.id_user is None

@pytest.mark.django_db
def test_execute_sync_issues_project_not_found():
    """Testa o comportamento quando o projeto não existe no banco"""
    strategy = SyncIssuesStrategy("email", "token", "http://fake-jira")
        
    synced_count = strategy.execute("NONEXISTENT")
    
    assert synced_count == 0

@pytest.mark.django_db
def test_execute_sync_issues_with_network_error():
    """Testa o tratamento de erro quando a API do Jira está indisponível"""
    strategy = SyncIssuesStrategy("email", "token", "http://fake-jira")
    
    project = Project.objects.create(
        jira_id=12345,
        key="PRJ",
        name="Test Project"
    )
    
    def mock_requests_get(url, params=None, auth=None, timeout=None):
        raise requests.exceptions.ConnectionError("Cannot connect to Jira API")
    
    with patch('requests.get', mock_requests_get):
        with pytest.raises(requests.exceptions.ConnectionError):
            strategy.execute("PRJ")
        
        assert Issue.objects.filter(project=project).count() == 0