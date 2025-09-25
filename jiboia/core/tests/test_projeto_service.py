from unittest.mock import MagicMock, patch, call
from datetime import date, timedelta

from jiboia.core.service.project_svc import list_projects_general, list_projects_especific

MOCK_TODAY = date(2025, 9, 24)

class MockProject:
    def __init__(self, id, project_id):
        self.id = id
        self.project_id = project_id
    
    def to_dict_json(self):
        return {"id": self.id, "project_id": self.project_id, "type": "BUG"}
    
class MockIssue:
    def __init__(self, id, project_id):
        self.id = id
        self.project_id = project_id
    
    def to_dict_json(self):
        return {"id": self.id, "project_id": self.project_id, "type": "BUG"}



@patch('jiboia.core.service.project_svc.date')
@patch('jiboia.core.models.Project.objects') 
def test_list_general_projects_with_3_months(mock_objects, mock_date):
    """
    Testa a função list_projects_general com issue_breakdown_months=3.
    Espera que a data de início (start_date) seja calculada corretamente.
    """

    mock_date.today.return_value = MOCK_TODAY

    mock_project_1 = MockProject(101, "P101")
    mock_project_2 = MockProject(102, "P102")

    mock_queryset = MagicMock()
    mock_queryset.filter.return_value = mock_queryset
    mock_queryset.order_by.return_value = [mock_project_1, mock_project_2]

    mock_objects.filter.return_value = mock_queryset

    issue_breakdown_months = 3
    result = list_projects_general(issue_breakdown_months)

    mock_objects.filter.assert_called_once_with(
        start_date_project__gte=date(2025, 7, 1)
    )

    mock_queryset.order_by.assert_called_once_with('-start_date_project')

    expected_result = [
        {"id": 101, "project_id": "P101", "type": "BUG"},
        {"id": 102, "project_id": "P102", "type": "BUG"}
    ]
    assert result == expected_result

@patch('jiboia.core.service.project_svc.date')
@patch('jiboia.core.models.Project.objects.filter')  
def test_list_general_projects_with_1_month(mock_filter, mock_date):
    """
    Testa list_projects_general com issue_breakdown_months=1.
    """

    mock_date.today.return_value = MOCK_TODAY
    EXPECTED_START_DATE = date(2025, 9, 1)

    mock_project_1 = MockProject(101, "P101")
    mock_project_2 = MockProject(102, "P102")

    mock_queryset = MagicMock()
    mock_queryset.order_by.return_value = [mock_project_1, mock_project_2]

    mock_filter.return_value = mock_queryset

    issue_breakdown_months = 1
    result = list_projects_general(issue_breakdown_months)

    mock_filter.assert_called_once_with(start_date_project__gte=EXPECTED_START_DATE)
    mock_queryset.order_by.assert_called_once_with('-start_date_project')

    expected_result = [
        {"id": 101, "project_id": "P101", "type": "BUG"},
        {"id": 102, "project_id": "P102", "type": "BUG"}
    ]
    assert result == expected_result

@patch('jiboia.core.service.project_svc.date')
@patch('jiboia.core.service.project_svc.Issue')
def test_list_issues_specific_with_3_months(mock_issue_class, mock_date):
    """
    Testa list_projects_especific com issue_breakdown_months=3.
    """

    mock_date.today.return_value = MOCK_TODAY

    EXPECTED_START_DATE = date(2025, 6, 1)
    EXPECTED_START_BURNDOWN = MOCK_TODAY - timedelta(days=2)

    mock_issue_1 = MockIssue(501, 10)
    mock_issue_2 = MockIssue(502, 10)

    mock_queryset_all = MagicMock()
    mock_queryset_all.__iter__.return_value = [mock_issue_1, mock_issue_2]
    mock_queryset_all.filter.side_effect = lambda **kwargs: mock_queryset_all

    mock_issue_class.objects.filter.return_value = mock_queryset_all

    project_id = 10
    issue_breakdown_months = 4
    burndown_days = 2
    result = list_projects_especific(project_id, issue_breakdown_months, burndown_days)

    expected_calls = [
        call(created_at__gte=EXPECTED_START_DATE),
        call(created_at__gte=EXPECTED_START_BURNDOWN),
    ]
    mock_queryset_all.filter.assert_has_calls(expected_calls, any_order=False)
    mock_issue_class.objects.filter.assert_called_once_with(project_id=project_id)


    expected_result = {
        "project_id": 10,
        "issues_per_month": [
            {"id": 501, "project_id": 10, "type": "BUG"},
            {"id": 502, "project_id": 10, "type": "BUG"}
        ],
        "issues_burndown": [
            {"id": 501, "project_id": 10, "type": "BUG"},
            {"id": 502, "project_id": 10, "type": "BUG"}
        ],
    }
    assert result == expected_result

@patch('jiboia.core.service.project_svc.date')
@patch('jiboia.core.service.project_svc.Issue')
def test_list_issues_specific_with_1_month(mock_issue_class, mock_date):
    """Testa list_projects_especific com issue_breakdown_months=1."""

    mock_date.today.return_value = MOCK_TODAY

    EXPECTED_START_DATE = date(2025, 9, 1)
    EXPECTED_START_BURNDOWN = MOCK_TODAY - timedelta(days=5)  

    mock_issue_3 = MockIssue(600, 20)
    mock_queryset_all = MagicMock()
    mock_queryset_all.filter.side_effect = lambda **kwargs: [mock_issue_3]
    mock_queryset_all.objects.filter.return_value = mock_queryset_all

    mock_issue_class.objects.filter.return_value = mock_queryset_all

    project_id = 20
    issue_breakdown_months = 1
    burndown_days = 5
    result = list_projects_especific(project_id, issue_breakdown_months, burndown_days)

    mock_issue_class.objects.filter.assert_called_once_with(project_id=project_id)

    expected_calls_queryset = [
        call(created_at__gte=EXPECTED_START_DATE),
        call(created_at__gte=EXPECTED_START_BURNDOWN),
    ]
    mock_queryset_all.filter.assert_has_calls(expected_calls_queryset, any_order=False)

    expected_result = {
        "project_id": 20,
        "issues_per_month": [
            {"id": 600, "project_id": 20, "type": "BUG"}
        ],
        "issues_burndown": [
            {"id": 600, "project_id": 20, "type": "BUG"}
        ],
    }
    assert result == expected_result
