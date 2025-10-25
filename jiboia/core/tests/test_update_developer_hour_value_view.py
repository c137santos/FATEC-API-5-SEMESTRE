import json
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from jiboia.core.models import Issue, Project, TimeLog

User = get_user_model()


@pytest.fixture
def setup_update_view_data():
    """Setup data for update hour value view tests"""
    developer = User.objects.create_user(
        username="developer",
        password="password123",
        first_name="Carlos",
        last_name="Silva",
        valor_hora=Decimal("50.00"),
    )

    project = Project.objects.create(
        key="PROJ",
        name="Project Test",
        description="Test project for view",
        jira_id=9100,
        uuid="test-uuid-100",
        projectTypeKey="software",
    )

    issue = Issue.objects.create(
        description="Test Issue",
        project=project,
        id_user=developer,
        time_estimate_seconds=14400,
        jira_id=8100,
    )

    TimeLog.objects.create(
        id_issue=issue,
        id_user=developer,
        seconds=14400,  # 4 hours
        description_log="Test work",
        jira_id=9600,
    )

    return {
        "developer": developer,
        "project": project,
        "issue": issue,
    }


@pytest.mark.django_db
def test_update_developer_hour_value_view_success(client, setup_update_view_data):
    """Test successful update through the view"""
    data = setup_update_view_data
    developer = data["developer"]
    project = data["project"]

    url = reverse(
        "update_developer_hour_value",
        kwargs={"project_id": project.id, "user_id": developer.id},
    )

    payload = {"valorHora": 85.50}

    response = client.patch(
        url,
        data=json.dumps(payload),
        content_type="application/json",
    )

    assert response.status_code == 200

    response_data = response.json()
    assert response_data["id"] == developer.id
    assert response_data["nome"] == "Carlos Silva"
    assert response_data["horasTrabalhadas"] == 4
    assert response_data["valorHora"] == 85.50

    # Verify database was updated
    developer.refresh_from_db()
    assert float(developer.valor_hora) == 85.50


@pytest.mark.django_db
def test_update_developer_hour_value_view_decimal_precision(client, setup_update_view_data):
    """Test update with decimal values"""
    data = setup_update_view_data
    developer = data["developer"]
    project = data["project"]

    url = reverse(
        "update_developer_hour_value",
        kwargs={"project_id": project.id, "user_id": developer.id},
    )

    payload = {"valorHora": 123.45}

    response = client.patch(
        url,
        data=json.dumps(payload),
        content_type="application/json",
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["valorHora"] == 123.45


@pytest.mark.django_db
def test_update_developer_hour_value_view_wrong_http_method(client, setup_update_view_data):
    """Test that only PATCH method is allowed"""
    data = setup_update_view_data
    developer = data["developer"]
    project = data["project"]

    url = reverse(
        "update_developer_hour_value",
        kwargs={"project_id": project.id, "user_id": developer.id},
    )

    payload = {"valorHora": 100.0}

    response = client.post(
        url,
        data=json.dumps(payload),
        content_type="application/json",
    )

    assert response.status_code == 405  # Method Not Allowed

    response = client.put(
        url,
        data=json.dumps(payload),
        content_type="application/json",
    )

    assert response.status_code == 405  # Method Not Allowed

    response = client.get(url)

    assert response.status_code == 405  # Method Not Allowed
