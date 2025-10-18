import pytest
from django.contrib.auth import get_user_model

from jiboia.core.models import Issue, Project
from jiboia.core.service.projects_svc import get_project_developers

User = get_user_model()


@pytest.mark.django_db
def test_get_project_developers_returns_empty_list_when_no_issues():
    project = Project.objects.create(
        key="EMPTY",
        name="Projeto Vazio",
        description="Projeto sem issues",
        jira_id=1001,
        uuid="uuid-empty",
        projectTypeKey="software",
    )

    result = get_project_developers(project.id)

    assert result == []


@pytest.mark.django_db
def test_get_project_developers_returns_empty_list_when_no_assigned_users():
    project = Project.objects.create(
        key="NOUSER",
        name="Projeto Sem User",
        description="Issues sem responsável",
        jira_id=1002,
        uuid="uuid-nouser",
        projectTypeKey="software",
    )

    Issue.objects.create(
        description="Issue sem responsável",
        project=project,
        time_estimate_seconds=3600,
        jira_id=2001,
    )

    result = get_project_developers(project.id)

    assert result == []


@pytest.mark.django_db
def test_get_project_developers_single_developer():
    user = User.objects.create_user(
        username="dev1",
        password="password123",
        first_name="João",
        last_name="Silva",
    )
    # Adiciona valor_hora se o campo existir
    if hasattr(user, "valor_hora"):
        user.valor_hora = 50.0
        user.save()

    project = Project.objects.create(
        key="SINGLE",
        name="Projeto Single Dev",
        description="Um desenvolvedor",
        jira_id=1003,
        uuid="uuid-single",
        projectTypeKey="software",
    )

    # Issue com 3600 segundos = 1 hora
    Issue.objects.create(
        description="Issue 1",
        project=project,
        id_user=user,
        time_estimate_seconds=3600,
        jira_id=2002,
    )

    # Issue com 7200 segundos = 2 horas
    Issue.objects.create(
        description="Issue 2",
        project=project,
        id_user=user,
        time_estimate_seconds=7200,
        jira_id=2003,
    )

    result = get_project_developers(project.id)

    assert len(result) == 1
    assert result[0]["id"] == user.id
    assert result[0]["nome"] == "João Silva"
    assert result[0]["horasTrabalhadas"] == 3  # 3600 + 7200 = 10800 segundos = 3 horas


@pytest.mark.django_db
def test_get_project_developers_multiple_developers_sorted():
    user1 = User.objects.create_user(
        username="dev1",
        password="pass",
        first_name="Maria",
        last_name="Santos",
    )
    user2 = User.objects.create_user(
        username="dev2",
        password="pass",
        first_name="Pedro",
        last_name="Oliveira",
    )
    user3 = User.objects.create_user(
        username="dev3",
        password="pass",
        first_name="Ana",
        last_name="Costa",
    )

    if hasattr(user1, "valor_hora"):
        user1.valor_hora = 100.0
        user1.save()
    if hasattr(user2, "valor_hora"):
        user2.valor_hora = 75.0
        user2.save()
    if hasattr(user3, "valor_hora"):
        user3.valor_hora = 50.0
        user3.save()

    project = Project.objects.create(
        key="MULTI",
        name="Projeto Multi Dev",
        description="Vários desenvolvedores",
        jira_id=1004,
        uuid="uuid-multi",
        projectTypeKey="software",
    )

    Issue.objects.create(
        description="Issue user1",
        project=project,
        id_user=user1,
        time_estimate_seconds=7200,
        jira_id=2004,
    )

    Issue.objects.create(
        description="Issue user2",
        project=project,
        id_user=user2,
        time_estimate_seconds=18000,
        jira_id=2005,
    )

    Issue.objects.create(
        description="Issue user3",
        project=project,
        id_user=user3,
        time_estimate_seconds=3600,
        jira_id=2006,
    )

    result = get_project_developers(project.id)

    assert len(result) == 3

    assert result[0]["id"] == user2.id
    assert result[0]["nome"] == "Pedro Oliveira"
    assert result[0]["horasTrabalhadas"] == 5

    assert result[1]["id"] == user1.id
    assert result[1]["nome"] == "Maria Santos"
    assert result[1]["horasTrabalhadas"] == 2

    assert result[2]["id"] == user3.id
    assert result[2]["nome"] == "Ana Costa"
    assert result[2]["horasTrabalhadas"] == 1


@pytest.mark.django_db
def test_get_project_developers_with_null_time_estimate():
    user = User.objects.create_user(
        username="dev1",
        password="pass",
        first_name="Carlos",
        last_name="Pereira",
    )

    project = Project.objects.create(
        key="NULL",
        name="Projeto Null Time",
        description="Issues com tempo nulo",
        jira_id=1005,
        uuid="uuid-null",
        projectTypeKey="software",
    )

    Issue.objects.create(
        description="Issue com tempo",
        project=project,
        id_user=user,
        time_estimate_seconds=3600,
        jira_id=2007,
    )

    Issue.objects.create(
        description="Issue sem tempo",
        project=project,
        id_user=user,
        time_estimate_seconds=None,
        jira_id=2008,
    )

    result = get_project_developers(project.id)

    assert len(result) == 1
    assert result[0]["id"] == user.id
    assert result[0]["horasTrabalhadas"] == 1


@pytest.mark.django_db
def test_get_project_developers_uses_username_when_no_full_name():
    user = User.objects.create_user(
        username="devuser",
        password="pass",
        first_name="",
        last_name="",
    )

    project = Project.objects.create(
        key="UNAME",
        name="Projeto Username",
        description="User sem nome completo",
        jira_id=1006,
        uuid="uuid-uname",
        projectTypeKey="software",
    )

    Issue.objects.create(
        description="Issue test",
        project=project,
        id_user=user,
        time_estimate_seconds=3600,
        jira_id=2009,
    )

    result = get_project_developers(project.id)

    assert len(result) == 1
    assert result[0]["nome"] == "devuser"


@pytest.mark.django_db
def test_get_project_developers_valor_hora_from_user():
    user = User.objects.create_user(
        username="dev_valor",
        password="pass",
        first_name="Lucas",
        last_name="Martins",
    )

    if hasattr(user, "valor_hora"):
        user.valor_hora = 125.50
        user.save()

    project = Project.objects.create(
        key="VALOR",
        name="Projeto Valor Hora",
        description="Teste valor hora",
        jira_id=1007,
        uuid="uuid-valor",
        projectTypeKey="software",
    )

    Issue.objects.create(
        description="Issue valor",
        project=project,
        id_user=user,
        time_estimate_seconds=3600,
        jira_id=2010,
    )

    result = get_project_developers(project.id)

    assert len(result) == 1
    if hasattr(user, "valor_hora"):
        assert result[0]["valorHora"] == 125.50
    else:
        assert result[0]["valorHora"] is None


@pytest.mark.django_db
def test_get_project_developers_rounding_hours():
    user = User.objects.create_user(username="dev_round", password="pass")

    project = Project.objects.create(
        key="ROUND",
        name="Projeto Round",
        description="Teste arredondamento",
        jira_id=1008,
        uuid="uuid-round",
        projectTypeKey="software",
    )

    Issue.objects.create(
        description="Issue round",
        project=project,
        id_user=user,
        time_estimate_seconds=5400,
        jira_id=2011,
    )

    result = get_project_developers(project.id)

    assert len(result) == 1
    assert result[0]["horasTrabalhadas"] == 2  # round(1.5) = 2


@pytest.mark.django_db
def test_get_project_developers_aggregates_multiple_issues_same_user():
    user = User.objects.create_user(
        username="dev_agg",
        password="pass",
        first_name="Fernanda",
        last_name="Lima",
    )

    project = Project.objects.create(
        key="AGG",
        name="Projeto Aggregation",
        description="Agregação de horas",
        jira_id=1009,
        uuid="uuid-agg",
        projectTypeKey="software",
    )

    for i in range(5):
        Issue.objects.create(
            description=f"Issue {i}",
            project=project,
            id_user=user,
            time_estimate_seconds=3600,
            jira_id=3000 + i,
        )

    result = get_project_developers(project.id)

    assert len(result) == 1
    assert result[0]["id"] == user.id
    assert result[0]["horasTrabalhadas"] == 5


@pytest.mark.django_db
def test_get_project_developers_different_projects_isolated():
    user1 = User.objects.create_user(username="dev1", password="pass")
    user2 = User.objects.create_user(username="dev2", password="pass")

    project_a = Project.objects.create(
        key="PROJA",
        name="Projeto A",
        description="Projeto A",
        jira_id=1010,
        uuid="uuid-a",
        projectTypeKey="software",
    )

    project_b = Project.objects.create(
        key="PROJB",
        name="Projeto B",
        description="Projeto B",
        jira_id=1011,
        uuid="uuid-b",
        projectTypeKey="software",
    )

    Issue.objects.create(
        description="Issue A",
        project=project_a,
        id_user=user1,
        time_estimate_seconds=3600,
        jira_id=4001,
    )

    Issue.objects.create(
        description="Issue B",
        project=project_b,
        id_user=user2,
        time_estimate_seconds=7200,
        jira_id=4002,
    )

    result_a = get_project_developers(project_a.id)
    result_b = get_project_developers(project_b.id)

    assert len(result_a) == 1
    assert result_a[0]["id"] == user1.id

    assert len(result_b) == 1
    assert result_b[0]["id"] == user2.id
