import json

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from jiboia.core.models import Issue, Project

User = get_user_model()


@pytest.fixture
def setup_developers_data():
    """
    Fixture que configura dados de teste para project_developers endpoint
    """
    # Cria usuários
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

    # Adiciona valor_hora se campo existir
    if hasattr(user1, "valor_hora"):
        user1.valor_hora = 6.0
        user1.save()
    if hasattr(user2, "valor_hora"):
        user2.valor_hora = 9.0
        user2.save()
    if hasattr(user3, "valor_hora"):
        user3.valor_hora = 16.0
        user3.save()

    # Cria projeto
    project = Project.objects.create(
        key="TEST",
        name="Projeto de Teste",
        description="Projeto para testar endpoint de desenvolvedores",
        jira_id=5001,
        uuid="test-devs-uuid",
        projectTypeKey="software",
    )

    # Cria issues com diferentes horas
    # user1: 159 horas = 572400 segundos
    Issue.objects.create(
        description="Issue Marília",
        project=project,
        id_user=user1,
        time_estimate_seconds=572400,
        jira_id=6001,
    )

    # user2: 237 horas = 853200 segundos
    Issue.objects.create(
        description="Issue Matheus",
        project=project,
        id_user=user2,
        time_estimate_seconds=853200,
        jira_id=6002,
    )

    # user3: 262 horas = 943200 segundos
    Issue.objects.create(
        description="Issue Clara",
        project=project,
        id_user=user3,
        time_estimate_seconds=943200,
        jira_id=6003,
    )

    return project


@pytest.mark.django_db
def test_project_developers_success_200(client, setup_developers_data):
    """
    Testa se o endpoint retorna 200 com sucesso e estrutura correta
    """
    project = setup_developers_data
    url = reverse("project_developers", kwargs={"project_id": project.id})

    response = client.get(url)

    assert response.status_code == 200

    data = json.loads(response.content)
    assert isinstance(data, list)


@pytest.mark.django_db
def test_project_developers_returns_correct_structure(client, setup_developers_data):
    """
    Testa se a estrutura de resposta está correta
    """
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
    """
    Testa se os desenvolvedores estão ordenados por horas trabalhadas (desc)
    """
    project = setup_developers_data
    url = reverse("project_developers", kwargs={"project_id": project.id})

    response = client.get(url)
    data = json.loads(response.content)

    assert len(data) == 3

    # Deve estar ordenado: Clara (262h), Matheus (237h), Marília (159h)
    assert data[0]["nome"] == "Clara Santos"
    assert data[0]["horasTrabalhadas"] == 262

    assert data[1]["nome"] == "Matheus Marciano"
    assert data[1]["horasTrabalhadas"] == 237

    assert data[2]["nome"] == "Marília Moraes"
    assert data[2]["horasTrabalhadas"] == 159


@pytest.mark.django_db
def test_project_developers_includes_valor_hora(client, setup_developers_data):
    """
    Testa se retorna o valor_hora quando disponível
    """
    project = setup_developers_data
    url = reverse("project_developers", kwargs={"project_id": project.id})

    response = client.get(url)
    data = json.loads(response.content)

    # Verifica se campo valor_hora existe no User model
    user = User.objects.first()
    if hasattr(user, "valor_hora"):
        # Se existe, deve retornar os valores configurados no fixture
        clara = next(d for d in data if "Clara" in d["nome"])
        matheus = next(d for d in data if "Matheus" in d["nome"])
        marilia = next(d for d in data if "Marília" in d["nome"])

        assert clara["valorHora"] == 16.0
        assert matheus["valorHora"] == 9.0
        assert marilia["valorHora"] == 6.0
    else:
        # Se não existe, deve retornar None
        for dev in data:
            assert dev["valorHora"] is None


@pytest.mark.django_db
def test_project_developers_empty_project(client):
    """
    Testa se retorna lista vazia para projeto sem issues
    """
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
    """
    Testa se retorna lista vazia quando issues não têm usuário responsável
    """
    project = Project.objects.create(
        key="NOUSER",
        name="Projeto Sem User",
        description="Issues sem responsável",
        jira_id=5003,
        uuid="nouser-uuid",
        projectTypeKey="software",
    )

    Issue.objects.create(
        description="Issue sem user",
        project=project,
        time_estimate_seconds=3600,
        jira_id=6004,
    )

    url = reverse("project_developers", kwargs={"project_id": project.id})
    response = client.get(url)

    assert response.status_code == 200

    data = json.loads(response.content)
    assert data == []


@pytest.mark.django_db
def test_project_developers_nonexistent_project(client):
    """
    Testa se endpoint retorna 200 com lista vazia para projeto inexistente
    """
    url = reverse("project_developers", kwargs={"project_id": 99999})
    response = client.get(url)

    assert response.status_code == 200

    data = json.loads(response.content)
    assert data == []


@pytest.mark.django_db
def test_project_developers_single_developer(client):
    """
    Testa se retorna corretamente quando há apenas um desenvolvedor
    """
    user = User.objects.create_user(
        username="solo_dev",
        password="pass",
        first_name="Solo",
        last_name="Developer",
    )

    if hasattr(user, "valor_hora"):
        user.valor_hora = 50.0
        user.save()

    project = Project.objects.create(
        key="SOLO",
        name="Projeto Solo",
        description="Um dev",
        jira_id=5004,
        uuid="solo-uuid",
        projectTypeKey="software",
    )

    Issue.objects.create(
        description="Issue solo",
        project=project,
        id_user=user,
        time_estimate_seconds=18000,  # 5 horas
        jira_id=6005,
    )

    url = reverse("project_developers", kwargs={"project_id": project.id})
    response = client.get(url)

    assert response.status_code == 200

    data = json.loads(response.content)
    assert len(data) == 1
    assert data[0]["nome"] == "Solo Developer"
    assert data[0]["horasTrabalhadas"] == 5


@pytest.mark.django_db
def test_project_developers_aggregates_multiple_issues(client):
    """
    Testa se agrega corretamente múltiplas issues do mesmo desenvolvedor
    """
    user = User.objects.create_user(
        username="multi_issue_dev",
        password="pass",
        first_name="Multi",
        last_name="Issue",
    )

    project = Project.objects.create(
        key="MULTI",
        name="Projeto Multi Issues",
        description="Múltiplas issues",
        jira_id=5005,
        uuid="multi-uuid",
        projectTypeKey="software",
    )

    # 3 issues de 2 horas cada = 6 horas total
    for i in range(3):
        Issue.objects.create(
            description=f"Issue {i}",
            project=project,
            id_user=user,
            time_estimate_seconds=7200,  # 2 horas
            jira_id=7000 + i,
        )

    url = reverse("project_developers", kwargs={"project_id": project.id})
    response = client.get(url)

    assert response.status_code == 200

    data = json.loads(response.content)
    assert len(data) == 1
    assert data[0]["horasTrabalhadas"] == 6


@pytest.mark.django_db
def test_project_developers_uses_username_fallback(client):
    """
    Testa se usa username quando não há nome completo
    """
    user = User.objects.create_user(
        username="username_only",
        password="pass",
        first_name="",
        last_name="",
    )

    project = Project.objects.create(
        key="UNAME",
        name="Projeto Username",
        description="Username fallback",
        jira_id=5006,
        uuid="uname-uuid",
        projectTypeKey="software",
    )

    Issue.objects.create(
        description="Issue username",
        project=project,
        id_user=user,
        time_estimate_seconds=3600,
        jira_id=6006,
    )

    url = reverse("project_developers", kwargs={"project_id": project.id})
    response = client.get(url)

    assert response.status_code == 200

    data = json.loads(response.content)
    assert len(data) == 1
    assert data[0]["nome"] == "username_only"


@pytest.mark.django_db
def test_project_developers_handles_zero_hours(client):
    """
    Testa se trata corretamente quando time_estimate_seconds é 0 ou None
    """
    user = User.objects.create_user(username="zero_dev", password="pass")

    project = Project.objects.create(
        key="ZERO",
        name="Projeto Zero",
        description="Tempo zero",
        jira_id=5007,
        uuid="zero-uuid",
        projectTypeKey="software",
    )

    # Issue com tempo 0
    Issue.objects.create(
        description="Issue zero",
        project=project,
        id_user=user,
        time_estimate_seconds=0,
        jira_id=6007,
    )

    # Issue com tempo None
    Issue.objects.create(
        description="Issue null",
        project=project,
        id_user=user,
        time_estimate_seconds=None,
        jira_id=6008,
    )

    url = reverse("project_developers", kwargs={"project_id": project.id})
    response = client.get(url)

    assert response.status_code == 200

    data = json.loads(response.content)
    assert len(data) == 1
    assert data[0]["horasTrabalhadas"] == 0


@pytest.mark.django_db
def test_project_developers_response_is_json_array(client):
    """
    Testa se a resposta é sempre um array JSON (mesmo vazio)
    """
    project = Project.objects.create(
        key="JSON",
        name="Projeto JSON",
        description="Teste JSON",
        jira_id=5008,
        uuid="json-uuid",
        projectTypeKey="software",
    )

    url = reverse("project_developers", kwargs={"project_id": project.id})
    response = client.get(url)

    assert response.status_code == 200
    assert response["Content-Type"] == "application/json"

    data = json.loads(response.content)
    assert isinstance(data, list)
