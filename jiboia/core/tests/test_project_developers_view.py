import json

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from jiboia.core.models import Issue, Project, TimeLog

User = get_user_model()


@pytest.fixture
def setup_developers_data():
    user1 = User.objects.create_user(
        username="marilia",
        password="password",
        first_name="Marília",
        last_name="Moraes",
    )
    user2 = User.objects.create_user(
        username="matheus",
        password="password",
        first_name="Matheus",
        last_name="Marciano",
    )
    user3 = User.objects.create_user(
        username="clara",
        password="password",
        first_name="Clara",
        last_name="Santos",
    )

    if hasattr(user1, "valor_hora"):
        user1.valor_hora = 6.0
        user1.save()
    if hasattr(user2, "valor_hora"):
        user2.valor_hora = 9.0
        user2.save()
    if hasattr(user3, "valor_hora"):
        user3.valor_hora = 16.0
        user3.save()

    project = Project.objects.create(
        key="TEST",
        name="Projeto de Teste",
        description="Projeto para testar endpoint de desenvolvedores",
        jira_id=5001,
        uuid="test-devs-uuid",
        projectTypeKey="software",
    )

    issue1 = Issue.objects.create(
        description="Issue Marília",
        project=project,
        id_user=user1,
        time_estimate_seconds=572400,
        jira_id=6001,
    )
    TimeLog.objects.create(
        id_issue=issue1,
        id_user=user1,
        seconds=572400,
        description_log="Trabalho da Marília",
        jira_id=7001,
    )

    issue2 = Issue.objects.create(
        description="Issue Matheus",
        project=project,
        id_user=user2,
        time_estimate_seconds=853200,
        jira_id=6002,
    )
    TimeLog.objects.create(
        id_issue=issue2,
        id_user=user2,
        seconds=853200,
        description_log="Trabalho do Matheus",
        jira_id=7002,
    )

    issue3 = Issue.objects.create(
        description="Issue Clara",
        project=project,
        id_user=user3,
        time_estimate_seconds=943200,
        jira_id=6003,
    )
    TimeLog.objects.create(
        id_issue=issue3,
        id_user=user3,
        seconds=943200,
        description_log="Trabalho da Clara",
        jira_id=7003,
    )

    return project


@pytest.mark.django_db
def test_project_developers_success_200(client, setup_developers_data):
    project = setup_developers_data
    url = reverse("project_developers", kwargs={"project_id": project.id})

    response = client.get(url)

    assert response.status_code == 200

    data = json.loads(response.content)
    assert isinstance(data, list)


@pytest.mark.django_db
def test_project_developers_returns_correct_structure(client, setup_developers_data):
    project = setup_developers_data
    url = reverse("project_developers", kwargs={"project_id": project.id})

    response = client.get(url)
    data = json.loads(response.content)

    assert len(data) == 3

    for dev in data:
        assert "id" in dev
        assert "nome" in dev
        assert "horasTrabalhadas" in dev
        assert "valorHora" in dev
        assert isinstance(dev["id"], int)
        assert isinstance(dev["nome"], str)
        assert isinstance(dev["horasTrabalhadas"], int)
        assert dev["valorHora"] is None or isinstance(dev["valorHora"], (int, float))


@pytest.mark.django_db
def test_project_developers_sorted_by_hours_desc(client, setup_developers_data):
    project = setup_developers_data
    url = reverse("project_developers", kwargs={"project_id": project.id})

    response = client.get(url)
    data = json.loads(response.content)

    assert len(data) == 3

    assert data[0]["nome"] == "Clara Santos"
    assert data[0]["horasTrabalhadas"] == 262

    assert data[1]["nome"] == "Matheus Marciano"
    assert data[1]["horasTrabalhadas"] == 237

    assert data[2]["nome"] == "Marília Moraes"
    assert data[2]["horasTrabalhadas"] == 159


@pytest.mark.django_db
def test_project_developers_includes_valor_hora(client, setup_developers_data):
    project = setup_developers_data
    url = reverse("project_developers", kwargs={"project_id": project.id})

    response = client.get(url)
    data = json.loads(response.content)

    user = User.objects.first()
    if hasattr(user, "valor_hora"):
        clara = next(d for d in data if "Clara" in d["nome"])
        matheus = next(d for d in data if "Matheus" in d["nome"])
        marilia = next(d for d in data if "Marília" in d["nome"])

        assert clara["valorHora"] == 16.0
        assert matheus["valorHora"] == 9.0
        assert marilia["valorHora"] == 6.0
    else:
        for dev in data:
            assert dev["valorHora"] is None


@pytest.mark.django_db
def test_project_developers_empty_project(client):
    project = Project.objects.create(
        key="EMPTY",
        name="Projeto Vazio",
        description="Sem issues",
        jira_id=5002,
        uuid="empty-uuid",
        projectTypeKey="software",
    )

    url = reverse("project_developers", kwargs={"project_id": project.id})
    response = client.get(url)

    assert response.status_code == 200

    data = json.loads(response.content)
    assert data == []


@pytest.mark.django_db
def test_project_developers_project_without_assigned_users(client):
    project = Project.objects.create(
        key="NOUSER",
        name="Projeto Sem User",
        description="Issues sem responsável",
        jira_id=5003,
        uuid="nouser-uuid",
        projectTypeKey="software",
    )

    issue = Issue.objects.create(
        description="Issue sem user",
        project=project,
        time_estimate_seconds=3600,
        jira_id=6004,
    )

    # TimeLog sem usuário - não deve aparecer no resultado
    TimeLog.objects.create(
        id_issue=issue,
        id_user=None,
        seconds=3600,
        description_log="Trabalho sem usuário atribuído",
        jira_id=7004,
    )

    url = reverse("project_developers", kwargs={"project_id": project.id})
    response = client.get(url)

    assert response.status_code == 200

    data = json.loads(response.content)
    assert data == []
