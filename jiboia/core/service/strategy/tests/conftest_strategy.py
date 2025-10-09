from unittest.mock import MagicMock

import pytest

from jiboia.core.models import IssueType, Project, StatusType
from jiboia.core.service.strategy.issues import SyncIssuesStrategy


@pytest.fixture
def sync_issues_strategy():
    return SyncIssuesStrategy('email@test.com', 'api_token', 'http://fake-jira.com')


@pytest.fixture
def mock_project():
    project = MagicMock(spec=Project)
    project.key = 'TEST'
    return project


@pytest.fixture
def mock_issue_type():
    issue_type = MagicMock(spec=IssueType)
    issue_type.jira_id = '10001'
    return issue_type


@pytest.fixture
def mock_status_type():
    status_type = MagicMock(spec=StatusType)
    status_type.jira_id = '1001'
    return status_type


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = 1
    return user


@pytest.fixture
def mock_issue_data():
    return {
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


@pytest.fixture
def mock_jira_response():
    return {
        "total": 2,
        "issues": [
            {"id": "10001", "fields": {}},
            {"id": "10002", "fields": {}}
        ]
    }

@pytest.fixture
def mock_issue_model():
    return MagicMock()