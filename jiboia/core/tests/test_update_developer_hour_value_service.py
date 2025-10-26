from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from jiboia.core.models import Issue, Project, TimeLog
from jiboia.core.service.projects_svc import update_developer_hour_value

User = get_user_model()


@pytest.fixture
def setup_update_hour_data():
    user = User.objects.create_user(
        username="developer",
        password="password123",
        first_name="João",
        last_name="Silva",
        valor_hora=Decimal("50.00"),
    )

    project = Project.objects.create(
        key="TESTPROJ",
        name="Test Project",
        description="Project for testing hour value update",
        jira_id=9001,
        uuid="test-uuid-001",
        projectTypeKey="software",
    )

    issue = Issue.objects.create(
        description="Test Issue",
        project=project,
        id_user=user,
        time_estimate_seconds=7200,
        jira_id=8001,
    )

    TimeLog.objects.create(
        id_issue=issue,
        id_user=user,
        seconds=7200,  # 2 hours
        description_log="Test work",
        jira_id=9501,
    )

    return {"user": user, "project": project, "issue": issue}


@pytest.mark.django_db
def test_update_developer_hour_value_success(setup_update_hour_data):
    """Test successful update of developer hourly rate"""
    data = setup_update_hour_data
    user = data["user"]
    project = data["project"]

    new_valor_hora = 75.50

    result = update_developer_hour_value(project.id, user.id, new_valor_hora)

    assert result["id"] == user.id
    assert result["nome"] == "João Silva"
    assert result["horasTrabalhadas"] == 2  # 7200 seconds = 2 hours
    assert result["valorHora"] == new_valor_hora

    user.refresh_from_db()
    assert float(user.valor_hora) == new_valor_hora


@pytest.mark.django_db
def test_update_developer_hour_value_with_zero(setup_update_hour_data):
    data = setup_update_hour_data
    user = data["user"]
    project = data["project"]

    new_valor_hora = 0.0

    result = update_developer_hour_value(project.id, user.id, new_valor_hora)

    assert result["valorHora"] == 0.0

    user.refresh_from_db()
    assert float(user.valor_hora) == 0.0


@pytest.mark.django_db
def test_update_developer_hour_value_project_not_found(setup_update_hour_data):
    data = setup_update_hour_data
    user = data["user"]

    invalid_project_id = 99999

    with pytest.raises(Project.DoesNotExist):
        update_developer_hour_value(invalid_project_id, user.id, 100.0)


@pytest.mark.django_db
def test_update_developer_hour_value_user_not_found(setup_update_hour_data):
    data = setup_update_hour_data
    project = data["project"]

    invalid_user_id = 99999

    with pytest.raises(User.DoesNotExist):
        update_developer_hour_value(project.id, invalid_user_id, 100.0)


@pytest.mark.django_db
def test_update_developer_hour_value_multiple_timelogs(setup_update_hour_data):
    data = setup_update_hour_data
    user = data["user"]
    project = data["project"]

    issue2 = Issue.objects.create(
        description="Test Issue 2",
        project=project,
        id_user=user,
        time_estimate_seconds=3600,
        jira_id=8002,
    )

    TimeLog.objects.create(
        id_issue=issue2,
        id_user=user,
        seconds=3600,
        description_log="More test work",
        jira_id=9502,
    )

    new_valor_hora = 80.0

    result = update_developer_hour_value(project.id, user.id, new_valor_hora)

    assert result["horasTrabalhadas"] == 3
    assert result["valorHora"] == new_valor_hora


@pytest.mark.django_db
def test_update_developer_hour_value_user_without_full_name(setup_update_hour_data):
    """Test update for user without first/last name (uses username)"""
    data = setup_update_hour_data
    project = data["project"]

    user_no_name = User.objects.create_user(
        username="devusername",
        password="password123",
        valor_hora=Decimal("45.00"),
    )

    issue = Issue.objects.create(
        description="Issue for user without name",
        project=project,
        id_user=user_no_name,
        time_estimate_seconds=3600,
        jira_id=8003,
    )

    TimeLog.objects.create(
        id_issue=issue,
        id_user=user_no_name,
        seconds=3600,
        description_log="Work by user without name",
        jira_id=9503,
    )

    new_valor_hora = 55.0

    result = update_developer_hour_value(project.id, user_no_name.id, new_valor_hora)

    assert result["nome"] == "devusername"
    assert result["valorHora"] == new_valor_hora


@pytest.mark.django_db
def test_update_developer_hour_value_decimal_precision(setup_update_hour_data):
    """Test update with decimal precision"""
    data = setup_update_hour_data
    user = data["user"]
    project = data["project"]

    new_valor_hora = 123.456

    result = update_developer_hour_value(project.id, user.id, new_valor_hora)

    assert result["valorHora"] == new_valor_hora

    user.refresh_from_db()
    assert float(user.valor_hora) == pytest.approx(new_valor_hora, rel=0.01)
