from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest
import requests

import jiboia.core.service.strategy.issues as issues_mod
from jiboia.core.models import Issue, IssueType, Project, StatusType
from jiboia.core.service.strategy.users import SyncUserStrategy


def test_update_project_dates():
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
            from django.db.models import Max, Min
            if isinstance(agg, Min):
                return {'start_date__min': min((i.start_date for i in self._issues if i.start_date), default=None)}
            if isinstance(agg, Max):
                return {'end_date__max': max((i.end_date for i in self._issues if i.end_date), default=None)}
            return {}
    
    class DummyProject:
        def __init__(self):
            self.start_date_project = None
            self.end_date_project = None
            self.saved = False
            self.issue_set = DummyQuerySet([
                DummyIssue(datetime(2023, 1, 1), datetime(2023, 1, 10)),
                DummyIssue(datetime(2023, 1, 5), datetime(2023, 1, 20)),
                DummyIssue(None, None),
            ])
        
        def save(self):
            self.saved = True

    project = DummyProject()
    issues_mod.SyncIssuesStrategy.update_project_dates(project)
    
    assert project.start_date_project == date(2023, 1, 1)
    assert project.end_date_project == date(2023, 1, 20)
    assert project.saved


def test_execute_issues():
    with patch('requests.get') as mock_requests_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"issues": [], "total": 0}
        mock_response.raise_for_status = MagicMock()
        mock_requests_get.return_value = mock_response
        
        with patch('jiboia.core.models.Project.objects.get') as mock_project_get, \
             patch.object(issues_mod.SyncIssuesStrategy, '_sync_issue') as mock_sync_issue, \
             patch.object(issues_mod.SyncIssuesStrategy, '_sync_worklogs') as _mock_sync_worklogs:

            dummy_project = MagicMock(spec=Project)
            mock_project_get.return_value = dummy_project
            mock_sync_issue.return_value = MagicMock(spec=Issue)

            strategy = issues_mod.SyncIssuesStrategy('email', 'token', 'http://fake-jira')
            result = strategy.execute('PRJ')
            
            assert isinstance(result, int)
            assert result >= 0

def test_execute_project_not_found():
    with patch('requests.get') as mock_requests_get:
        with patch('jiboia.core.models.Project.objects.get') as mock_project_get:
            mock_project_get.side_effect = Project.DoesNotExist

            strategy = issues_mod.SyncIssuesStrategy('email', 'token', 'http://fake-jira')
            result = strategy.execute('NONEXISTENT')
            
            assert result == 0
            mock_requests_get.assert_not_called()

def test_execute_successful_sync():
    with patch('requests.get') as mock_requests_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total": 2,
            "issues": [
                {"id": "10001", "fields": {}},
                {"id": "10002", "fields": {}}
            ]
        }
        mock_requests_get.return_value = mock_response
        
        with patch('jiboia.core.models.Project.objects.get') as mock_project_get, \
             patch.object(issues_mod.SyncIssuesStrategy, '_sync_issue') as mock_sync_issue, \
             patch.object(issues_mod.SyncIssuesStrategy, '_sync_worklogs') as mock_sync_worklogs, \
             patch.object(issues_mod.SyncIssuesStrategy, 'update_project_dates') as mock_update_dates:

            mock_project = MagicMock(spec=Project)
            mock_project_get.return_value = mock_project
            mock_sync_issue.return_value = MagicMock(spec=Issue)

            strategy = issues_mod.SyncIssuesStrategy('email', 'token', 'http://fake-jira')
            result = strategy.execute('TEST')

            assert result == 2
            mock_project_get.assert_called_once_with(key='TEST')
            mock_update_dates.assert_called_once_with(mock_project)
            assert mock_sync_issue.call_count == 2
            assert mock_sync_worklogs.call_count == 2
            mock_requests_get.assert_called()


def test_sync_issue_creation():
    with patch.object(SyncUserStrategy, 'execute') as mock_sync_user, \
         patch('jiboia.core.models.IssueType.objects.get') as mock_issue_type_get, \
         patch('jiboia.core.models.StatusType.objects.get') as mock_status_type_get, \
         patch('jiboia.core.models.Issue.objects.update_or_create') as mock_issue_update:

        mock_user = MagicMock()
        mock_sync_user.return_value = mock_user
        
        mock_issue_type = MagicMock(spec=IssueType)
        mock_issue_type_get.return_value = mock_issue_type
        
        mock_status_type = MagicMock(spec=StatusType)
        mock_status_type_get.return_value = mock_status_type
        
        mock_issue = MagicMock(spec=Issue)
        mock_issue_update.return_value = (mock_issue, True)

        strategy = issues_mod.SyncIssuesStrategy('email', 'token', 'http://fake-jira')
        
        mock_project = MagicMock(spec=Project)
        mock_issue_data = {
            'id': '10001',
            'fields': {
                'assignee': {'accountId': 'user123'},
                'issuetype': {'id': '10001'},
                'status': {'id': '1001'},
                'summary': 'Test Issue',
                'description': {
                    'content': [{
                        'content': [{'text': 'Issue description'}]
                    }]
                },
                'created': '2023-01-01T00:00:00.000Z',
                'resolutiondate': '2023-01-10T00:00:00.000Z',
                'timeestimate': 3600,
                'customfield_10015': '2023-01-02T00:00:00.000Z',
                'worklog': {'worklogs': []}
            }
        }

        result = strategy._sync_issue(mock_issue_data, mock_project)

        assert result is not None
        mock_issue_update.assert_called_once()
        
def test_execute_api_error():
    strategy = issues_mod.SyncIssuesStrategy('email', 'token', 'http://fake-jira')
    
    with patch('jiboia.core.models.Project.objects.get') as mock_project_get, \
         patch.object(strategy, '_make_request') as mock_make_request:
        
        mock_project_get.return_value = MagicMock(spec=Project)
        mock_make_request.side_effect = requests.RequestException("API Error")
        
        with pytest.raises(requests.RequestException):
            strategy.execute('TEST')