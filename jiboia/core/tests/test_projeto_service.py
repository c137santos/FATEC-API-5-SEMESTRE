from unittest.mock import MagicMock

from jiboia.core.service.project_svc import list_projects_general


def test_list_projects_general_success(
    mock_today,
    projects_and_issues,
    setup_project_order,
    setup_issue_queryset,
    setup_statuslog_mock,
    setup_timelog_mock,
):
    project_a, project_b, issue_a1, issue_b1, all_issues = projects_and_issues
    setup_project_order(project_b, project_a)
    setup_issue_queryset(all_issues, project_a, project_b, issue_a1, issue_b1)
    setup_statuslog_mock()
    setup_timelog_mock()

    result = list_projects_general(2)

    expected_issues_per_month = [
        {"date": "08/2025", "pending": 0, "on_going": 0, "mr": 0, "concluded": 1},
        {"date": "09/2025", "pending": 1, "on_going": 0, "mr": 0, "concluded": 0},
    ]
    assert result["issues_per_month"] == expected_issues_per_month

    expected_projects = [
        {
            "project_id": 2,
            "name": "Project Beta",
            "total_hours": 1800,
            "total_issues": 1,
            "dev_hours": [{"dev_id": 1, "name": "dev1", "hours": 1800}],
        },
        {
            "project_id": 1,
            "name": "Project Alpha",
            "total_hours": 10800,
            "total_issues": 1,
            "dev_hours": [
                {"dev_id": 1, "name": "dev1", "hours": 3600},
                {"dev_id": 2, "name": "dev2", "hours": 7200},
            ],
        },
    ]
    assert result["projects"] == expected_projects

def test_list_projects_general_empty_data(mock_managers):
    """
    Testa o cenário em que não há projetos, issues ou logs no período.
    O resultado esperado é uma estrutura válida, mas vazia (ou com zeros).
    """

    mock_managers["project"].filter.return_value.order_by.return_value = []

    mock_issue_queryset = MagicMock()
    mock_issue_queryset.all.return_value = []
    mock_managers["issue"].filter.return_value = mock_issue_queryset
    
    mock_managers["statuslog"].filter.return_value.count.return_value = 0

    mock_timelog_queryset = MagicMock()
    mock_timelog_queryset.aggregate.return_value = {"total": None}
    mock_timelog_queryset.values.return_value.annotate.return_value = []
    mock_managers["timelog"].filter.return_value = mock_timelog_queryset

    mock_issue_queryset.filter.return_value.count.return_value = 0

    issue_breakdown_months = 3
    result = list_projects_general(issue_breakdown_months)

    expected_issues_per_month = [
        {
            "date": "07/2025",
            "pending": 0,
            "on_going": 0,
            "mr": 0,
            "concluded": 0,
        },
        {
            "date": "08/2025",
            "pending": 0,
            "on_going": 0,
            "mr": 0,
            "concluded": 0,
        },
        {
            "date": "09/2025",
            "pending": 0,
            "on_going": 0,
            "mr": 0,
            "concluded": 0,
        },
    ]
    assert result["issues_per_month"] == expected_issues_per_month

    assert result["projects"] == []