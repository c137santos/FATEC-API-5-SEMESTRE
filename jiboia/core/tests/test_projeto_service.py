from datetime import date, datetime

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from freezegun import freeze_time

from jiboia.core.models import Issue, Project, StatusLog, StatusType, TimeLog
from jiboia.core.service.project_svc import list_projects_general


@pytest.mark.django_db
@freeze_time("2025-09-24")
def test_list_projects_general_success():
    user = get_user_model()
    developer_one = user.objects.create_user(username="dev1", password="x")
    developer_two = user.objects.create_user(username="dev2", password="x")

    status_pending = StatusType.objects.create(key="k1", name="pending", jira_id=1)
    status_ongoing = StatusType.objects.create(key="k2", name="on_going", jira_id=2)
    status_mr = StatusType.objects.create(key="k3", name="mr", jira_id=3)
    status_concluded = StatusType.objects.create(key="k4", name="concluded", jira_id=4)

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

    issue_alpha_1 = Issue.objects.create(description="ia1", project=project_alpha)
    issue_beta_1 = Issue.objects.create(description="ib1", project=project_beta)

    Issue.objects.filter(pk=issue_alpha_1.id).update(
        created_at=timezone.make_aware(datetime(2025, 8, 5, 10, 0))
    )
    Issue.objects.filter(pk=issue_beta_1.id).update(
        created_at=timezone.make_aware(datetime(2025, 9, 10, 10, 0))
    )

    StatusLog.objects.create(id_issue=issue_alpha_1, new_status=status_concluded)
    StatusLog.objects.create(id_issue=issue_beta_1, new_status=status_pending)

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
        {"date": "08/2025", "pending": 0, "on_going": 0, "mr": 0, "concluded": 1},
        {"date": "09/2025", "pending": 1, "on_going": 0, "mr": 0, "concluded": 0},
    ]

    assert result["projects"] == [
        {
            "project_id": project_beta.id,
            "name": "Project Beta",
            "total_hours": 1800,
            "total_issues": 1,
            "dev_hours": [
                {"dev_id": developer_one.id, "name": developer_one.username, "hours": 1800}
            ],
        },
        {
            "project_id": project_alpha.id,
            "name": "Project Alpha",
            "total_hours": 10800,
            "total_issues": 1,
            "dev_hours": [
                {"dev_id": developer_one.id, "name": developer_one.username, "hours": 3600},
                {"dev_id": developer_two.id, "name": developer_two.username, "hours": 7200},
            ],
        },
    ]


@pytest.mark.django_db
@freeze_time("2025-09-24")
def test_list_projects_general_empty_data():
    StatusType.objects.create(key="k1", name="pending", jira_id=1)
    StatusType.objects.create(key="k2", name="on_going", jira_id=2)
    StatusType.objects.create(key="k3", name="mr", jira_id=3)
    StatusType.objects.create(key="k4", name="concluded", jira_id=4)

    result = list_projects_general(3)

    assert result["issues_per_month"] == [
        {"date": "07/2025", "pending": 0, "on_going": 0, "mr": 0, "concluded": 0},
        {"date": "08/2025", "pending": 0, "on_going": 0, "mr": 0, "concluded": 0},
        {"date": "09/2025", "pending": 0, "on_going": 0, "mr": 0, "concluded": 0},
    ]
    assert result["projects"] == []
