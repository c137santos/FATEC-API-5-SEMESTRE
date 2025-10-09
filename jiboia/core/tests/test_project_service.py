from datetime import date, datetime

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from freezegun import freeze_time

from jiboia.core.models import Issue, Project, StatusType, TimeLog
from jiboia.core.service.projects_svc import list_projects_general, save_projects


@pytest.mark.django_db
def test_save_projects_creates_new_projects():
    projects_data = [
        {
            "jira_id": 1,
            "key": "PROJ1",
            "name": "Projeto 1",
            "description": "Desc 1",
            "start_date_project": "2024-01-01",
            "end_date_project": "2024-12-31",
            "uuid": "uiahisuah",
            "projectTypeKey": "software",
        },
        {
            "jira_id": 2,
            "key": "PROJ2",
            "name": "Projeto 2",
            "description": "Desc 2",
            "start_date_project": "2024-02-01",
            "end_date_project": "2024-11-30",
            "uuid": "aloualoui",
            "projectTypeKey": "business",
        },
    ]

    save_projects(projects_data)

    assert Project.objects.count() == 2
    proj1 = Project.objects.get(jira_id=1)
    assert proj1.name == "Projeto 1"
    assert proj1.description == "Desc 1"
    assert str(proj1.start_date_project) == "2024-01-01"
    assert str(proj1.end_date_project) == "2024-12-31"
    assert proj1.uuid == "uiahisuah"
    assert proj1.projectTypeKey == "software"

    proj2 = Project.objects.get(jira_id=2)
    assert proj2.name == "Projeto 2"
    assert proj2.description == "Desc 2"
    assert str(proj2.start_date_project) == "2024-02-01"
    assert str(proj2.end_date_project) == "2024-11-30"
    assert proj2.uuid == "aloualoui"
    assert proj2.projectTypeKey == "business"


@pytest.mark.django_db
def test_save_projects_updates_existing_project():
    Project.objects.create(
        jira_id=1,
        key="PROJ1",
        name="Projeto Antigo",
        description="Desc Antiga",
        start_date_project="2024-01-01",
        end_date_project="2024-12-31",
        uuid=101,
        projectTypeKey="software",
    )

    projects_data = [
        {
            "jira_id": 1,
            "key": "PROJ1",
            "name": "Projeto Atualizado",
            "description": "Nova descrição",
            "start_date_project": "2024-01-01",
            "end_date_project": "2024-12-31",
            "uuid": "101",
            "projectTypeKey": "software",
        }
    ]

    save_projects(projects_data)

    proj = Project.objects.get(jira_id=1)
    assert proj.name == "Projeto Atualizado"
    assert proj.description


@pytest.mark.django_db
@freeze_time("2025-09-24")
def test_list_projects_general_success():
    user = get_user_model()
    developer_one = user.objects.create_user(username="dev1", password="x")
    developer_two = user.objects.create_user(username="dev2", password="x")

    statuses = [
        ("pending", 1),
        ("on_going", 2),
        ("mr", 3),
        ("concluded", 4),
    ]
    for name, jira_id in statuses:
        StatusType.objects.create(key=f"k{jira_id}", name=name, jira_id=jira_id)

    concluded_status = StatusType.objects.get(name="concluded")
    pending_status = StatusType.objects.get(name="pending")

    project_alpha = Project.objects.create(
        key="ALPHA",
        name="Project Alpha",
        description="",
        start_date_project=date(2025, 8, 15),
        uuid=1001,
        jira_id=2001,
    )
    project_beta = Project.objects.create(
        key="BETA",
        name="Project Beta",
        description="",
        start_date_project=date(2025, 9, 1),
        uuid=1002,
        jira_id=2002,
    )

    issue_alpha_1 = Issue.objects.create(description="ia1", project=project_alpha, status=concluded_status)
    issue_beta_1 = Issue.objects.create(description="ib1", project=project_beta, status=pending_status)

    Issue.objects.filter(pk=issue_alpha_1.id).update(created_at=timezone.make_aware(datetime(2025, 8, 5, 10, 0)))
    Issue.objects.filter(pk=issue_beta_1.id).update(created_at=timezone.make_aware(datetime(2025, 9, 10, 10, 0)))

    TimeLog.objects.create(
        id_issue=issue_alpha_1,
        id_user=developer_one,
        seconds=3600,
        description_log="a1-1",
        jira_id=3001,
    )
    TimeLog.objects.create(
        id_issue=issue_alpha_1,
        id_user=developer_two,
        seconds=7200,
        description_log="a1-2",
        jira_id=3002,
    )
    TimeLog.objects.create(
        id_issue=issue_beta_1,
        id_user=developer_one,
        seconds=1800,
        description_log="b1-1",
        jira_id=3003,
    )

    result = list_projects_general(2)

    assert result["issues_per_month"] == [
        {"date": "2025-08-01", "pending": 0, "on_going": 0, "mr": 0, "concluded": 1},
        {"date": "2025-09-01", "pending": 1, "on_going": 0, "mr": 0, "concluded": 0},
    ]

    projects_result = result["projects"]

    assert len(projects_result) == 2

    alpha_project = next(p for p in projects_result if p["project_id"] == project_alpha.id)
    beta_project = next(p for p in projects_result if p["project_id"] == project_beta.id)

    assert alpha_project == {
        "project_id": project_alpha.id,
        "name": "Project Alpha",
        "total_hours": 3.0,
        "total_issues": 1,
        "dev_hours": [
            {"dev_id": developer_one.id, "name": developer_one.username, "hours": 1.0},
            {"dev_id": developer_two.id, "name": developer_two.username, "hours": 2.0},
        ],
    }

    assert beta_project == {
        "project_id": project_beta.id,
        "name": "Project Beta",
        "total_hours": 0.5,
        "total_issues": 1,
        "dev_hours": [{"dev_id": developer_one.id, "name": developer_one.username, "hours": 0.5}],
    }


@pytest.mark.django_db
@freeze_time("2025-09-24")
def test_list_projects_general_empty_data():
    statuses = [
        ("pending", 1),
        ("on_going", 2),
        ("mr", 3),
        ("concluded", 4),
    ]
    for name, jira_id in statuses:
        StatusType.objects.create(key=f"k{jira_id}", name=name, jira_id=jira_id)

    result = list_projects_general(3)

    assert result["issues_per_month"] == [
        {"date": "2025-07-01", "pending": 0, "on_going": 0, "mr": 0, "concluded": 0},
        {"date": "2025-08-01", "pending": 0, "on_going": 0, "mr": 0, "concluded": 0},
        {"date": "2025-09-01", "pending": 0, "on_going": 0, "mr": 0, "concluded": 0},
    ]
    assert result["projects"] == []
