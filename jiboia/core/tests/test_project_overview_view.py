import json

import pytest
from django.urls import reverse
from django.utils import timezone

from jiboia.core.models import Issue, IssueType, Project, StatusType


@pytest.fixture
def setup_project_data(db):
    """
    Configura dados de teste para os testes da view de project_overview
    """
    project = Project.objects.create(
        key="TEST",
        name="Projeto de Teste View",
        description="Projeto para testes da view",
        jira_id=501,
        uuid="test-view-uuid",
        projectTypeKey="software",
    )

    pending_status = StatusType.objects.create(key="pending", name="Pendente", jira_id=601)
    in_progress_status = StatusType.objects.create(key="in_progress", name="Em Andamento", jira_id=602)

    task_type = IssueType.objects.create(name="Task", description="Tarefa", jira_id=701)

    Issue.objects.create(
        description="Issue de teste 1",
        project=project,
        status=pending_status,
        type_issue=task_type,
        created_at=timezone.now(),
    )

    Issue.objects.create(
        description="Issue de teste 2",
        project=project,
        status=in_progress_status,
        type_issue=task_type,
        created_at=timezone.now(),
    )

    return project


@pytest.mark.django_db
def test_project_overview_view_success(authenticated_client, setup_project_data):
    """
    Testa se a view de project_overview retorna 200 e os dados corretos
    """
    project = setup_project_data

    url = reverse("project_overview", kwargs={"project_id": project.id})
    response = authenticated_client.get(url)

    assert response.status_code == 200

    data = json.loads(response.content)
    assert data["project_id"] == project.id
    assert data["name"] == project.name
    assert "issues_per_month" in data
    assert "issues_today" in data
    assert "burndown" in data


@pytest.mark.django_db
def test_project_overview_view_with_parameters(authenticated_client, setup_project_data):
    """
    Testa se a view de project_overview aceita e processa os parâmetros
    """
    project = setup_project_data

    url = reverse("project_overview", kwargs={"project_id": project.id})
    response = authenticated_client.get(f"{url}?issues_breakdown_months=3&burdown_days=2")

    assert response.status_code == 200

    data = json.loads(response.content)
    assert len(data["issues_per_month"]) == 3
    assert len(data["burndown"]["pending_per_day"]) == 2


@pytest.mark.django_db
def test_project_overview_view_invalid_parameters(authenticated_client, setup_project_data):
    """
    Testa se a view de project_overview valida corretamente os parâmetros
    """
    project = setup_project_data

    url = reverse("project_overview", kwargs={"project_id": project.id})
    response = authenticated_client.get(f"{url}?issues_breakdown_months=abc&burdown_days=xyz")

    assert response.status_code == 400

    data = json.loads(response.content)
    assert "error" in data


@pytest.mark.django_db
def test_project_overview_view_project_not_found(authenticated_client):
    """
    Testa se a view de project_overview retorna 404 quando o projeto não existe
    """
    url = reverse("project_overview", kwargs={"project_id": 9999})
    response = authenticated_client.get(url)

    assert response.status_code == 404

    data = json.loads(response.content)
    assert "error" in data
