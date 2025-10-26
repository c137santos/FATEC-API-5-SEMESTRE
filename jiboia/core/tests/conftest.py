from datetime import date, timedelta

import pytest
from django.utils import timezone

from jiboia.core.models import Issue, IssueType, Project, StatusType

MOCK_TODAY = date(2025, 9, 24)


@pytest.fixture
def setup_issues_data(db):
    """
    Configura dados de teste básicos para os testes da view de list_paginable_issues
    """
    project = Project.objects.create(
        key="TEST",
        name="Projeto de Teste",
        description="Projeto para testes",
        jira_id=502,
        uuid="test-uuid",
        projectTypeKey="software",
        start_date_project=date(2025, 1, 1),
        end_date_project=(timezone.now() + timedelta(days=1)).date(),
    )

    status = StatusType.objects.create(key="pending", name="Pendente", jira_id=601)
    issue_type = IssueType.objects.create(name="Task", description="Tarefa", jira_id=701)

    for i in range(5):
        Issue.objects.create(
            description=f"Issue de teste {i+1}",
            project=project,
            status=status,
            type_issue=issue_type,
            jira_id=1000 + i,
            time_estimate_seconds=3600 * i,
        )

    return project
