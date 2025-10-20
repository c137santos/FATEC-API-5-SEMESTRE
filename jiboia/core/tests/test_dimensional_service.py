from datetime import datetime

import pytest
from django.utils import timezone

from jiboia.accounts.models import User
from jiboia.core.models import (
    DimDev,
    DimProjeto,
    DimStatus,
    DimTipoIssue,
    FatoEsforco,
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
def test_generate_project_snapshot_data_creates_snapshots():
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

    DimenssionalService.generate_project_snapshot_data(TipoGranularidade.DIA)

    assert FatoProjetoSnapshot.objects.count() == 1
    snap = FatoProjetoSnapshot.objects.first()
    assert snap.projeto.nome_projeto == "Projeto Teste"
    assert snap.intervalo_snapshot.tipo_granularidade == TipoGranularidade.DIA.value
    assert snap.custo_projeto_atual_rs >= 0
    assert snap.total_minutos_acumulados >= 0


@pytest.mark.django_db
def test_generate_project_snapshot_data_multiple_projects():
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

    DimenssionalService.generate_project_snapshot_data(TipoGranularidade.DIA)
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

    DimenssionalService.generate_fact_issue(TipoGranularidade.DIA)
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


@pytest.mark.django_db
def test_generate_fact_worlog():
    dev = User.objects.create_user(
        username="yan",
        first_name="Jon",
        last_name="Snow",
        email="jon@example.com",
        password="snow",
        valor_hora=60,
        jira_id=1,
    )
    dev2 = User.objects.create_user(
        username="jon2",
        first_name="Jon",
        last_name="Snow",
        email="jon2@example.com",
        password="snow",
        valor_hora=50,
        jira_id=2,
    )

    DimDev.objects.create(
        id_dev_jiba=dev.id,
        id_dev_jira=dev.jira_id,
        nome_dev=dev.username,
        valor_hora=dev.valor_hora,
    )

    DimDev.objects.create(
        id_dev_jiba=dev2.id,
        id_dev_jira=dev2.jira_id,
        nome_dev=dev2.username,
        valor_hora=dev2.valor_hora,
    )
    issue_type_bug = IssueType.objects.create(name="Bug", description="Bug Issue", subtask=False, jira_id=101)

    DimTipoIssue.objects.create(
        id_tipo_jira=issue_type_bug.jira_id,
        id_tipo_jiba=issue_type_bug.id,
        nome_tipo=issue_type_bug.name,
    )

    status_type_open = StatusType.objects.create(name="Open", key="op", jira_id=201)
    DimStatus.objects.create(
        id_status_jira=status_type_open.jira_id,
        id_status_jiba=status_type_open.id,
        nome_status=status_type_open.name,
    )
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
    project = Project.objects.create(
        key="PPP",
        name="Projeto Teste",
        description="Desc",
        start_date_project=timezone.now().date(),
        end_date_project=timezone.now().date(),
        uuid="uuid2",
        jira_id=2,
        projectTypeKey="software",
    )
    DimProjeto.objects.create(
        id_projeto_jiba=projeto.id,
        id_projeto_jira=projeto.jira_id,
        data_inicio=projeto.start_date_project,
        nome_projeto=projeto.name,
    )

    DimProjeto.objects.create(
        id_projeto_jiba=project.id,
        id_projeto_jira=project.jira_id,
        data_inicio=project.start_date_project,
        nome_projeto=project.name,
    )

    issue1 = Issue.objects.create(
        description="Issue projeto teste",
        project=projeto,
        time_estimate_seconds=3600,
        jira_id=2021,
        type_issue=issue_type_bug,
        status=status_type_open,
    )
    issue2 = Issue.objects.create(
        description="Issue projeto OUTRO",
        project=projeto,
        time_estimate_seconds=3600,
        jira_id=2021,
        type_issue=issue_type_bug,
        status=status_type_open,
    )
    Issue.objects.create(
        description="Issue projeto teste",
        project=projeto,
        time_estimate_seconds=3600,
        jira_id=2020,
        type_issue=issue_type_bug,
        status=status_type_open,
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
        type_issue=issue_type_bug,
        status=status_type_open,
    )

    log_date = timezone.now()
    log_date_ontem = datetime(1999, 1, 1)
    TimeLog.objects.create(id_user=dev, id_issue=issue1, seconds=1200, log_date=log_date, jira_id=444)
    TimeLog.objects.create(id_user=dev, id_issue=issue2, seconds=2400, log_date=log_date, jira_id=555)
    a = TimeLog.objects.create(id_user=dev2, id_issue=issue1, seconds=10000, log_date=log_date_ontem, jira_id=666)
    a.log_date = log_date_ontem
    a.save()
    success = DimenssionalService.generate_fact_worklog(TipoGranularidade.DIA)

    assert success is True

    fato_dev1 = FatoEsforco.objects.filter(dev__id_dev_jira=dev.jira_id)
    fato_dev2 = FatoEsforco.objects.filter(dev__id_dev_jira=dev2.jira_id)

    assert len(FatoEsforco.objects.filter().all()) == 2
    assert len(fato_dev1) == 2
    assert len(fato_dev2) == 0
    assert fato_dev1[0].minutos_acumulados == 20
    assert fato_dev1[1].minutos_acumulados == 40
    assert fato_dev1[0].minutos_acumulados + fato_dev1[1].minutos_acumulados == 60
