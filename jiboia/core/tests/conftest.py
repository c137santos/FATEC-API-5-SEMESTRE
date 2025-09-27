from datetime import date
from unittest.mock import MagicMock, patch

import pytest

MOCK_TODAY = date(2025, 9, 24)

@pytest.fixture
def mock_project_model():
    """Simulate the classs Project."""
    class MockProject:
        def __init__(self, id, name, start_date_project):
            self.id = id
            self.name = name
            self.start_date_project = start_date_project
    return MockProject

@pytest.fixture
def mock_issue_model():
    """Simulate the classs Issue."""
    class MockIssue:
        def __init__(self, id, project_id, created_at):
            self.id = id
            self.project_id = project_id
            self.created_at = created_at
            self.project = MagicMock(id=project_id) 
            self.statuslog_set = MagicMock() 

    return MockIssue

@pytest.fixture
def mock_timelog_model():
    """Simulate the classs TimeLog."""
    class MockTimeLog:
        def __init__(self, id, id_issue_id, id_user_id, id_user__username, seconds):
            self.id = id
            self.id_issue_id = id_issue_id
            self.id_user_id = id_user_id
            self.id_user__username = id_user__username
            self.seconds = seconds
    return MockTimeLog

@pytest.fixture
def mock_statuslog_model():
    """Simulate the classs StatusLog."""
    class MockStatusLog:
        def __init__(self, id, id_issue, new_status_name):
            self.id = id
            self.id_issue = id_issue
            self.new_status = MagicMock(name=new_status_name) 
    return MockStatusLog

@pytest.fixture
def mock_managers():
    with (
        patch("jiboia.core.service.project_svc.Project.objects") as mock_project_manager,
        patch("jiboia.core.service.project_svc.Issue.objects") as mock_issue_manager,
        patch("jiboia.core.service.project_svc.TimeLog.objects") as mock_timelog_manager,
        patch("jiboia.core.service.project_svc.StatusLog.objects") as mock_statuslog_manager,
    ):
        yield {
            "project": mock_project_manager,
            "issue": mock_issue_manager,
            "timelog": mock_timelog_manager,
            "statuslog": mock_statuslog_manager,
        }
        
@pytest.fixture
def projects_and_issues(mock_project_model, mock_issue_model):
    project_a = mock_project_model(id=1, name="Project Alpha", start_date_project=date(2025, 8, 15))
    project_b = mock_project_model(id=2, name="Project Beta", start_date_project=date(2025, 9, 1))
    
    issue_a1 = mock_issue_model(id=101, project_id=1, created_at=date(2025, 8, 5), status_name="concluded")
    issue_b1 = mock_issue_model(id=102, project_id=2, created_at=date(2025, 9, 10), status_name="pending")
    
    return project_a, project_b, issue_a1, issue_b1, [issue_a1, issue_b1]


@pytest.fixture
def setup_project_order(mock_managers):
    def _apply(project_b, project_a):
        mock_managers["project"].filter.return_value.order_by.return_value = [project_b, project_a]
    return _apply


def _mock_issues_monthly_side_effect(issue_a1, issue_b1, **kwargs):
    if kwargs.get("created_at__month") == 8:
        return [issue_a1]
    if kwargs.get("created_at__month") == 9:
        return [issue_b1]
    return []


def _mock_issues_project_side_effect(project_a, project_b, issue_a1, issue_b1, **kwargs):
    project = kwargs.get("project")
    if project == project_a:
        result = [issue_a1]
    elif project == project_b:
        result = [issue_b1]
    else:
        result = []
    mock_qs = MagicMock(spec=list, return_value=result)
    mock_qs.__iter__.side_effect = lambda: iter(result)
    mock_qs.count.return_value = len(result)
    return mock_qs


@pytest.fixture
def setup_issue_queryset(mock_managers):
    def _apply(all_issues, project_a, project_b, issue_a1, issue_b1):
        mock_issues_start_date = MagicMock()
        mock_issues_start_date.all.return_value = all_issues
        mock_managers["issue"].filter.return_value = mock_issues_start_date

        def issues_filter_side_effect(**kwargs):
            if "created_at__month" in kwargs:
                return _mock_issues_monthly_side_effect(issue_a1, issue_b1, **kwargs)
            if "project" in kwargs:
                return _mock_issues_project_side_effect(project_a, project_b, issue_a1, issue_b1, **kwargs)
            return MagicMock(count=lambda: 0)

        mock_issues_start_date.filter.side_effect = issues_filter_side_effect
    return _apply