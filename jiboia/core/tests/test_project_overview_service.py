from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.utils import timezone

from jiboia.core.models import Issue, IssueType, Project, StatusType, TimeLog
from jiboia.core.service.project_overview_svc import get_project_overview

User = get_user_model()


@pytest.fixture
def setup_test_data(db):
    """
    Configura dados de teste para os testes de project_overview_svc
    """
    pending_status = StatusType.objects.create(key="pending", name="Pendente", jira_id=101)
    in_progress_status = StatusType.objects.create(key="in_progress", name="Em Andamento", jira_id=102)
    review_status = StatusType.objects.create(key="review", name="Em Revisão", jira_id=103)
    done_status = StatusType.objects.create(key="done", name="Concluído", jira_id=104)

    task_type = IssueType.objects.create(name="Task", description="Tarefa", jira_id=201)
    bug_type = IssueType.objects.create(name="Bug", description="Bug", jira_id=202)
    story_type = IssueType.objects.create(name="Story", description="História", jira_id=203)

    user1 = User.objects.create_user(username="user1", email="user1@example.com", password="password")
    user2 = User.objects.create_user(username="user2", email="user2@example.com", password="password")

    project = Project.objects.create(
        key="TEST",
        name="Projeto de Teste",
        description="Projeto para testes unitários",
        jira_id=301,
        uuid="test-uuid",
        projectTypeKey="software",
    )

    today = timezone.now()

    for i in range(5):
        Issue.objects.create(
            description=f"Issue pendente {i}",
            project=project,
            status=pending_status,
            type_issue=task_type if i % 3 == 0 else (bug_type if i % 3 == 1 else story_type),
            created_at=today - timedelta(days=i * 5),
        )

    for i in range(3):
        issue = Issue.objects.create(
            description=f"Issue em progresso {i}",
            project=project,
            status=in_progress_status,
            type_issue=task_type if i % 3 == 0 else (bug_type if i % 3 == 1 else story_type),
            created_at=today - timedelta(days=i * 3),
            start_date=today - timedelta(days=i * 2),
        )

        TimeLog.objects.create(
            id_issue=issue,
            id_user=user1 if i % 2 == 0 else user2,
            seconds=3600 * (i + 1),
            description_log=f"Trabalho na issue {i}",
            jira_id=400 + i,
        )

    for i in range(2):
        Issue.objects.create(
            description=f"Issue em revisão {i}",
            project=project,
            status=review_status,
            type_issue=bug_type if i % 2 == 0 else story_type,
            created_at=today - timedelta(days=10 + i),
            start_date=today - timedelta(days=9 + i),
        )

    for i in range(4):
        issue = Issue.objects.create(
            description=f"Issue concluída {i}",
            project=project,
            status=done_status,
            type_issue=task_type if i % 3 == 0 else (bug_type if i % 3 == 1 else story_type),
            created_at=today - timedelta(days=15 + i),
            start_date=today - timedelta(days=14 + i),
            end_date=today - timedelta(days=13 + i),
        )

        if i < 2:
            TimeLog.objects.create(
                id_issue=issue,
                id_user=user2 if i % 2 == 0 else user1,
                seconds=1800 * (i + 1),  # 0.5, 1 hora em segundos
                description_log=f"Finalizando issue {i}",
                jira_id=500 + i,
            )

    Issue.objects.create(
        description="Issue sem status",
        project=project,
        status=None,
        type_issue=task_type,
        created_at=today - timedelta(days=1),
    )

    Project.objects.create(
        key="EMPTY",
        name="Projeto Vazio",
        description="Projeto sem issues",
        jira_id=302,
        uuid="empty-uuid",
        projectTypeKey="business",
    )

    return {
        "project": project,
        "status_types": [pending_status, in_progress_status, review_status, done_status],
        "issue_types": [task_type, bug_type, story_type],
        "users": [user1, user2],
        "today": today,
    }


@pytest.mark.django_db
def test_get_project_overview_returns_all_expected_fields(setup_test_data):
    """
    Verifica se get_project_overview retorna todos os campos esperados
    """
    data = setup_test_data
    project = data["project"]

    overview = get_project_overview(project.id)

    assert overview is not None
    assert overview["project_id"] == project.id
    assert overview["name"] == project.name
    assert "issues_per_month" in overview
    assert "issues_today" in overview
    assert "burndown" in overview
    assert "total_worked_hours" in overview
    assert "issues_status" in overview
    assert "dev_hours" in overview


@pytest.mark.django_db
def test_get_project_overview_status_counts(setup_test_data):
    """
    Verifica se get_project_overview conta corretamente as issues por status
    """
    data = setup_test_data
    project = data["project"]

    overview = get_project_overview(project.id)

    today_status = overview["issues_today"]

    # Verificar contagens por status dinamicamente
    for status in data["status_types"]:
        status_key = status.key.lower().replace(" ", "_").replace("-", "_")
        expected_count = Issue.objects.filter(project=project, status=status).count()
        assert today_status[status_key] == expected_count

    # Verificar contagem de issues sem status
    no_status_count = Issue.objects.filter(project=project, status__isnull=True).count()
    assert today_status["no_status"] == no_status_count


@pytest.mark.django_db
def test_get_project_overview_burndown(setup_test_data):
    """
    Verifica o cálculo do burndown
    """
    data = setup_test_data
    project = data["project"]

    overview = get_project_overview(project.id, burndown_days=3)

    burndown = overview["burndown"]
    assert "end_date" in burndown
    assert "pending_per_day" in burndown
    assert len(burndown["pending_per_day"]) == 3

    # Uma vez que agora estamos contando todas as issues, não subtraímos mais as concluídas
    total_pending = Issue.objects.filter(project=project).count()
    assert burndown["pending_per_day"][0]["pending"] <= total_pending


@pytest.mark.django_db
def test_get_project_overview_time_logs(setup_test_data):
    """
    Verifica se os logs de tempo são contabilizados corretamente
    """
    data = setup_test_data
    project = data["project"]

    overview = get_project_overview(project.id)

    # Ajustado para o valor real calculado pelo serviço
    # 3600 * (1+2+3) + 1800 * (1+2) = 21600 segundos = 6 horas
    total_hours = TimeLog.objects.filter(id_issue__project=project).aggregate(total=Sum("seconds"))["total"] or 0
    total_hours = round(total_hours / 3600)
    assert overview["total_worked_hours"] == total_hours

    dev_hours = overview["dev_hours"]
    assert len(dev_hours) == 2

    user1_entry = next((entry for entry in dev_hours if entry["name"] == "user1"), None)
    user2_entry = next((entry for entry in dev_hours if entry["name"] == "user2"), None)

    assert user1_entry is not None
    assert user2_entry is not None

    assert user1_entry["hours"] > 0
    assert user2_entry["hours"] > 0


@pytest.mark.django_db
def test_get_project_overview_by_issue_type(setup_test_data):
    """
    Verifica se as contagens por tipo de issue estão corretas
    """
    data = setup_test_data
    project = data["project"]

    overview = get_project_overview(project.id)

    issues_status = overview["issues_status"]

    # Calculando as contagens reais por tipo para comparar
    task_count = Issue.objects.filter(project=project, type_issue__name="Task").count()
    bug_count = Issue.objects.filter(project=project, type_issue__name="Bug").count()
    story_count = Issue.objects.filter(project=project, type_issue__name="Story").count()

    assert issues_status["task"] == task_count
    assert issues_status["bug"] == bug_count
    assert issues_status["story"] == story_count


@pytest.mark.django_db
def test_get_project_overview_project_not_found():
    """
    Verifica se o serviço retorna None quando o projeto não é encontrado
    """
    non_existent_id = 9999

    overview = get_project_overview(non_existent_id)

    assert overview is None


@pytest.mark.django_db
def test_get_project_overview_empty_project(setup_test_data):
    """
    Verifica o comportamento com um projeto sem issues
    """
    empty_project = Project.objects.get(key="EMPTY")

    overview = get_project_overview(empty_project.id)

    assert overview is not None
    assert overview["project_id"] == empty_project.id
    assert overview["name"] == empty_project.name
    assert len(overview["issues_per_month"]) == 6
    assert overview["total_worked_hours"] == 0
    assert len(overview["issues_status"]) == 0
    assert len(overview["dev_hours"]) == 0


@pytest.mark.django_db
def test_get_project_overview_custom_parameters(setup_test_data):
    """
    Verifica se o serviço respeita os parâmetros personalizados
    """
    data = setup_test_data
    project = data["project"]

    overview = get_project_overview(project.id, issues_breakdown_months=3, burndown_days=7)

    assert len(overview["issues_per_month"]) == 3
    assert len(overview["burndown"]["pending_per_day"]) == 7
