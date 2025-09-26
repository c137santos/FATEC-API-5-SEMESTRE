import pytest
from datetime import date
from unittest.mock import patch, MagicMock

MOCK_TODAY = date(2025, 9, 24)

@pytest.fixture
def mock_today():
    """Mocka date.today() para retornar uma data fixa."""
    with patch("jiboia.core.service.project_svc.date") as mock_date:
        mock_date.today.return_value = MOCK_TODAY
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)
        yield mock_date

@pytest.fixture
def mock_project_model():
    """Simula a classe Project."""
    class MockProject:
        def __init__(self, id, name, start_date_project):
            self.id = id
            self.name = name
            self.start_date_project = start_date_project
    return MockProject

@pytest.fixture
def mock_issue_model():
    """Simula a classe Issue."""
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
    """Simula a classe TimeLog."""
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
    """Simula a classe StatusLog."""
    class MockStatusLog:
        def __init__(self, id, id_issue, new_status_name):
            self.id = id
            self.id_issue = id_issue
            self.new_status = MagicMock(name=new_status_name) # Simula o objeto de status
    return MockStatusLog

@pytest.fixture
def mock_managers():
    """Patch em todos os managers de Models do Django usados na função."""
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


# ---- Fixtures auxiliares para o teste de projeto_svc ----

@pytest.fixture
def projects_and_issues(mock_project_model, mock_issue_model):
    project_a = mock_project_model(id=1, name="Project Alpha", start_date_project=date(2025, 8, 15))
    project_b = mock_project_model(id=2, name="Project Beta", start_date_project=date(2025, 9, 1))
    issue_a1 = mock_issue_model(id=101, project_id=1, created_at=date(2025, 8, 5))
    issue_b1 = mock_issue_model(id=102, project_id=2, created_at=date(2025, 9, 10))
    return project_a, project_b, issue_a1, issue_b1, [issue_a1, issue_b1]


@pytest.fixture
def setup_project_order(mock_managers):
    def _apply(project_b, project_a):
        mock_managers["project"].filter.return_value.order_by.return_value = [project_b, project_a]
    return _apply


@pytest.fixture
def setup_issue_queryset(mock_managers):
    def _apply(all_issues, project_a, project_b, issue_a1, issue_b1):
        mock_issues_start_date = MagicMock()
        mock_issues_start_date.all.return_value = all_issues
        mock_managers["issue"].filter.return_value = mock_issues_start_date

        def mock_issues_monthly_side_effect(**kwargs):
            if kwargs.get("created_at__month") == 8:
                return [issue_a1]
            if kwargs.get("created_at__month") == 9:
                return [issue_b1]
            return []

        def mock_issues_project_side_effect(**kwargs):
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

        def issues_filter_side_effect(**kwargs):
            if "created_at__month" in kwargs:
                return mock_issues_monthly_side_effect(**kwargs)
            if "project" in kwargs:
                return mock_issues_project_side_effect(**kwargs)
            return MagicMock(count=lambda: 0)

        mock_issues_start_date.filter.side_effect = issues_filter_side_effect
    return _apply


@pytest.fixture
def setup_statuslog_mock(mock_managers):
    def _apply():
        def mock_status_count_side_effect(**kwargs):
            issue_list = kwargs.get("id_issue__in", [])
            new_status = kwargs.get("new_status__name")
            mock_count = MagicMock()

            try:
                issue_ids_as_set = {i.id for i in issue_list}
            except AttributeError:
                issue_ids_as_set = set(issue_list)

            if issue_ids_as_set == {101}:
                if new_status == "concluded":
                    mock_count.count.return_value = 1
                else:
                    mock_count.count.return_value = 0
            elif issue_ids_as_set == {102}:
                if new_status == "pending":
                    mock_count.count.return_value = 1
                else:
                    mock_count.count.return_value = 0
            else:
                mock_count.count.return_value = 0

            return mock_count

        mock_managers["statuslog"].filter.side_effect = mock_status_count_side_effect
    return _apply


@pytest.fixture
def setup_timelog_mock(mock_managers):
    def _apply():
        def mock_timelog_filter_side_effect(id_issue__in):
            mock_qs = MagicMock()

            try:
                issue_ids_as_set = {i.id for i in id_issue__in}
            except (AttributeError, TypeError):
                issue_ids_as_set = {i for i in id_issue__in if isinstance(i, int) or getattr(i, "id", None) is not None}
            except Exception:
                issue_ids_as_set = set()

            if issue_ids_as_set == {101}:
                mock_qs.aggregate.return_value = {"total": 10800}
                dev_hours_result = [
                    {"id_user_id": 1, "id_user__username": "dev1", "hours": 3600},
                    {"id_user_id": 2, "id_user__username": "dev2", "hours": 7200},
                ]
                values_result_mock = MagicMock()
                values_result_mock.annotate.return_value = dev_hours_result
                mock_qs.values.return_value = values_result_mock
            elif issue_ids_as_set == {102}:
                mock_qs.aggregate.return_value = {"total": 1800}
                dev_hours_result = [
                    {"id_user_id": 1, "id_user__username": "dev1", "hours": 1800},
                ]
                values_result_mock = MagicMock()
                values_result_mock.annotate.return_value = dev_hours_result
                mock_qs.values.return_value = values_result_mock
            else:
                mock_qs.aggregate.return_value = {"total": None}
                mock_qs.values.return_value.annotate.return_value = []

            return mock_qs

        mock_managers["timelog"].filter.side_effect = mock_timelog_filter_side_effect
    return _apply