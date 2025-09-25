import pytest
from datetime import date
from unittest.mock import MagicMock, call, patch
from jiboia.core.models import Issue
from jiboia.core.service.project_svc import list_projects_general, list_projects_especific

@pytest.mark.usefixtures("mock_today")
def test_list_general_projects_with_3_months(mock_project, mock_project_objects):
    mock_objects, mock_queryset = mock_project_objects

    mock_project_1 = mock_project(101, "P101")
    mock_project_2 = mock_project(102, "P102")
    mock_queryset.order_by.return_value = [mock_project_1, mock_project_2]

    issue_breakdown_months = 3
    result = list_projects_general(issue_breakdown_months)

    mock_objects.filter.assert_called_once_with(start_date_project__gte=date(2025, 7, 1))
    mock_queryset.order_by.assert_called_once_with('-start_date_project')

    expected_result = [
        {"id": 101, "project_id": "P101", "type": "BUG"},
        {"id": 102, "project_id": "P102", "type": "BUG"}
    ]
    assert result == expected_result

@pytest.mark.usefixtures("mock_today")
def test_list_general_projects_with_1_month(mock_project, mock_project_objects):
    mock_objects, mock_queryset = mock_project_objects

    EXPECTED_START_DATE = date(2025, 9, 1)

    mock_project_1 = mock_project(101, "P101")
    mock_project_2 = mock_project(102, "P102")
    mock_queryset.order_by.return_value = [mock_project_1, mock_project_2]

    issue_breakdown_months = 1
    result = list_projects_general(issue_breakdown_months)

    mock_objects.filter.assert_called_once_with(start_date_project__gte=EXPECTED_START_DATE)
    mock_queryset.order_by.assert_called_once_with('-start_date_project')

    expected_result = [
        {"id": 101, "project_id": "P101", "type": "BUG"},
        {"id": 102, "project_id": "P102", "type": "BUG"}
    ]
    assert result == expected_result

@pytest.mark.usefixtures("mock_today")
def test_list_issues_specific_with_3_months(mock_issue):
    EXPECTED_START_DATE = date(2025, 6, 1)
    EXPECTED_START_BURNDOWN = date(2025, 9, 22)

    mock_issue_1 = mock_issue(501, 10)
    mock_issue_2 = mock_issue(502, 10)

    mock_queryset_all = MagicMock()
    mock_queryset_all.__iter__.return_value = [mock_issue_1, mock_issue_2]
    mock_queryset_all.filter.side_effect = lambda **kwargs: mock_queryset_all
    mock_queryset_all.order_by.return_value = [mock_issue_1, mock_issue_2]

    with patch("jiboia.core.models.Issue.objects") as mock_manager:
        mock_manager.filter.return_value = mock_queryset_all

        project_id = 10
        issue_breakdown_months = 4
        burndown_days = 2
        result = list_projects_especific(project_id, issue_breakdown_months, burndown_days)

        mock_manager.filter.assert_called_once_with(project_id=project_id)
        expected_calls_queryset = [
            call(created_at__gte=EXPECTED_START_DATE),
            call(created_at__gte=EXPECTED_START_BURNDOWN),
        ]
        mock_queryset_all.filter.assert_has_calls(expected_calls_queryset, any_order=False)

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

@pytest.mark.usefixtures("mock_today")
def test_list_issues_specific_with_1_month(mock_issue):
    EXPECTED_START_DATE = date(2025, 9, 1)
    EXPECTED_START_BURNDOWN = date(2025, 9, 19)

    mock_issue_3 = mock_issue(600, 20)

    mock_queryset_all = MagicMock()
    mock_queryset_all.__iter__.return_value = [mock_issue_3]
    mock_queryset_all.filter.side_effect = lambda **kwargs: mock_queryset_all
    mock_queryset_all.order_by.return_value = [mock_issue_3]

    with patch("jiboia.core.models.Issue.objects") as mock_manager:
        mock_manager.filter.return_value = mock_queryset_all

        project_id = 20
        issue_breakdown_months = 1
        burndown_days = 5
        result = list_projects_especific(project_id, issue_breakdown_months, burndown_days)

        Issue.objects.filter.assert_called_once_with(project_id=project_id)
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
