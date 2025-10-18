import pytest
from django.utils import timezone

from jiboia.core.models import (
    FatoIssue,
    FatoProjetoSnapshot,
    Issue,
    IssueType,
    Project,
    StatusType,
    TimeLog,
)
from jiboia.core.service.dimensional_svc import DimenssionalService, TipoGranularidade


@pytest.mark.django_db
def test_load_fato_projeto_snapshot_creates_snapshots():
    projeto = Project.objects.create(
        key="PRJ1",
        name="Projeto Teste",
        description="Desc",
        start_date_project=timezone.now().date(),
        end_date_project=timezone.now().date(),
        uuid="uuid1",
        jira_id=1,
        projectTypeKey="software",
    )
    issue = Issue.objects.create(
        description="Issue 1", created_at=timezone.now(), project=projeto, time_estimate_seconds=3600, jira_id=2020
    )
    TimeLog.objects.create(id_issue=issue, seconds=1800, log_date=timezone.now(), jira_id=issue.id)

    DimenssionalService.load_fato_projeto_snapshot(TipoGranularidade.DIA)

    assert FatoProjetoSnapshot.objects.count() == 1
    snap = FatoProjetoSnapshot.objects.first()
    assert snap.projeto.nome_projeto == "Projeto Teste"
    assert snap.intervalo_snapshot.tipo_granularidade == TipoGranularidade.DIA.value
    assert snap.custo_projeto_atual_rs >= 0
    assert snap.total_minutos_acumulados >= 0


@pytest.mark.django_db
def test_load_fato_projeto_snapshot_multiple_projects():
    projeto1 = Project.objects.create(
        key="PRJ1",
        name="Projeto 1",
        description="Desc",
        start_date_project=timezone.now().date(),
        end_date_project=timezone.now().date(),
        uuid="uuid1",
        jira_id=1,
        projectTypeKey="software",
    )
    projeto2 = Project.objects.create(
        key="PRJ2",
        name="Projeto 2",
        description="Desc",
        start_date_project=timezone.now().date(),
        end_date_project=timezone.now().date(),
        uuid="uuid2",
        jira_id=2,
        projectTypeKey="software",
    )
    Issue.objects.create(description="Issue 1", created_at=timezone.now(), project=projeto1, time_estimate_seconds=3600)
    Issue.objects.create(description="Issue 2", created_at=timezone.now(), project=projeto2, time_estimate_seconds=7200)

    DimenssionalService.load_fato_projeto_snapshot(TipoGranularidade.DIA)
    assert FatoProjetoSnapshot.objects.count() == 2
    nomes = set(FatoProjetoSnapshot.objects.values_list("projeto__nome_projeto", flat=True))
    assert "Projeto 1" in nomes
    assert "Projeto 2" in nomes


@pytest.mark.django_db
def test_load_fato_issue():
    issue_type_bug = IssueType.objects.create(name="Bug", description="Bug Issue", subtask=False, jira_id=101)
    issue_type_history = IssueType.objects.create(
        name="History", description="History Issue", subtask=False, jira_id=102
    )
    status_type_open = StatusType.objects.create(name="Open", key="op", jira_id=201)
    status_type_done = StatusType.objects.create(name="Done", key="dn", jira_id=200)
    projeto = Project.objects.create(
        key="PRJ1",
        name="Projeto Teste",
        description="Desc",
        start_date_project=timezone.now().date(),
        end_date_project=timezone.now().date(),
        uuid="uuid1",
        jira_id=1,
        projectTypeKey="software",
    )
    Project.objects.create(
        key="PPP",
        name="Projeto Teste",
        description="Desc",
        start_date_project=timezone.now().date(),
        end_date_project=timezone.now().date(),
        uuid="uuid2",
        jira_id=2,
        projectTypeKey="software",
    )
    Issue.objects.create(
        description="Issue projeto teste",
        project=projeto,
        time_estimate_seconds=3600,
        jira_id=2021,
        type_issue=issue_type_history,
        status=status_type_open,
    )
    Issue.objects.create(
        description="Issue projeto OUTRO",
        project=projeto,
        time_estimate_seconds=3600,
        jira_id=2021,
        type_issue=issue_type_history,
        status=status_type_open,
    )
    Issue.objects.create(
        description="Issue projeto teste",
        project=projeto,
        time_estimate_seconds=3600,
        jira_id=2020,
        type_issue=issue_type_bug,
        status=status_type_done,
    )
    Issue.objects.create(
        description="Issue projeto teste",
        project=projeto,
        time_estimate_seconds=3600,
        jira_id=2022,
        type_issue=issue_type_bug,
        status=status_type_open,
    )
    Issue.objects.create(
        description="Issue projeto teste",
        project=projeto,
        time_estimate_seconds=3600,
        jira_id=2023,
        type_issue=issue_type_history,
        status=status_type_done,
    )

    DimenssionalService.load_fact_issue(TipoGranularidade.DIA)
    assert FatoIssue.objects.count() == 8
    fato_bug_open = FatoIssue.objects.filter(
        tipo_issue__nome_tipo="Bug", status__nome_status="Open", projeto__id=projeto.id
    ).all()
    assert fato_bug_open.count() == 1
    assert fato_bug_open[0].total_issue == 1

    fato_bug_done = FatoIssue.objects.filter(
        tipo_issue__nome_tipo="Bug", status__nome_status="Done", projeto__id=projeto.id
    ).all()
    assert fato_bug_done.count() == 1
    assert fato_bug_done[0].total_issue == 1

    fato_history_open = FatoIssue.objects.filter(
        tipo_issue__nome_tipo="History", status__nome_status="Open", projeto__id=projeto.id
    ).all()
    assert fato_history_open.count() == 1
    assert fato_history_open[0].total_issue == 2

    fato_history_done = FatoIssue.objects.filter(
        tipo_issue__nome_tipo="History", status__nome_status="Done", projeto__id=projeto.id
    ).all()
    assert fato_history_done.count() == 1
    assert fato_history_done[0].total_issue == 1
